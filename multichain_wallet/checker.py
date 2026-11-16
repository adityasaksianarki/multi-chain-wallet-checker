"""Core wallet balance checker — EVM, Solana, and Bitcoin."""

from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass, field
from typing import Optional

import requests
from web3 import Web3

from multichain_wallet.chains import CHAINS, Chain
from multichain_wallet.validation import validate_address


@dataclass
class BalanceResult:
    chain: str
    symbol: str
    balance: float
    explorer_url: str
    error: Optional[str] = None


@dataclass
class WalletSummary:
    address: str
    results: list[BalanceResult] = field(default_factory=list)
    total_chains_checked: int = 0
    errors: int = 0

    @property
    def non_zero(self) -> list[BalanceResult]:
        return [r for r in self.results if r.balance > 0]


class WalletChecker:
    """Query balances across multiple blockchains.

    Usage::

        checker = WalletChecker()
        summary = checker.check_all("0xabc...")
        for r in summary.non_zero:
            print(f"{r.chain}: {r.balance:.6f} {r.symbol}")
    """

    def __init__(self, chains: Optional[list[str]] = None, timeout: int = 15):
        self.timeout = timeout
        if chains is None:
            self.chains = list(CHAINS.keys())
        else:
            self.chains = [c.lower() for c in chains]
            unknown = set(self.chains) - set(CHAINS)
            if unknown:
                raise ValueError(f"Unknown chains: {unknown}. Available: {list(CHAINS.keys())}")

    # ── Public API ──────────────────────────────────────────────────────

    def check_all(self, address: str, max_workers: int = 8) -> WalletSummary:
        """Check balances on all configured chains in parallel.

        Raises ValueError up front if the address is not valid for any of
        the selected chain types, instead of collecting one RPC error
        per chain.
        """
        validate_address(address, self.chains)
        summary = WalletSummary(address=address)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {
                pool.submit(self._check_single, address, name): name
                for name in self.chains
            }
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                summary.results.append(result)
                summary.total_chains_checked += 1
                if result.error:
                    summary.errors += 1

        # Sort by chain name for consistent output
        summary.results.sort(key=lambda r: r.chain)
        return summary

    def check(self, address: str, chain: str) -> BalanceResult:
        """Check balance on a single chain.

        Raises ValueError if the address is not valid for that chain's
        type.
        """
        chain = chain.lower()
        if chain not in CHAINS:
            return BalanceResult(
                chain=chain, symbol="?", balance=0,
                explorer_url="", error=f"Unknown chain: {chain}",
            )
        validate_address(address, [chain])
        return self._check_single(address, chain)

    # ── Internal ────────────────────────────────────────────────────────

    def _check_single(self, address: str, chain_name: str) -> BalanceResult:
        c = CHAINS[chain_name]
        try:
            if c.is_evm:
                balance = self._evm_balance(address, c)
            elif chain_name == "solana":
                balance = self._solana_balance(address, c)
            elif chain_name == "bitcoin":
                balance = self._bitcoin_balance(address, c)
            else:
                return BalanceResult(
                    chain=c.name, symbol=c.symbol, balance=0,
                    explorer_url="", error="Unsupported chain type",
                )

            explorer = f"{c.explorer}/address/{address}"
            return BalanceResult(
                chain=c.name, symbol=c.symbol,
                balance=balance, explorer_url=explorer,
            )
        except Exception as exc:
            return BalanceResult(
                chain=c.name, symbol=c.symbol, balance=0,
                explorer_url="", error=str(exc),
            )

    def _evm_balance(self, address: str, chain: Chain) -> float:
        w3 = Web3(Web3.HTTPProvider(chain.rpc_url, request_kwargs={"timeout": self.timeout}))
        if not w3.is_connected():
            raise ConnectionError(f"Cannot connect to {chain.name} RPC")
        checksum = Web3.to_checksum_address(address)
        wei = w3.eth.get_balance(checksum)
        return float(Web3.from_wei(wei, "ether"))

    def _solana_balance(self, address: str, chain: Chain) -> float:
        payload = {
            "jsonrpc": "2.0", "id": 1, "method": "getBalance",
            "params": [address],
        }
        resp = requests.post(chain.rpc_url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(data["error"].get("message", "RPC error"))
        lamports = data["result"]["value"]
        return lamports / 10 ** chain.decimals

    def _bitcoin_balance(self, address: str, chain: Chain) -> float:
        url = f"{chain.rpc_url}/address/{address}"
        resp = requests.get(url, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        # blockstream returns funded - spent in satoshis
        stats = data.get("chain_stats", {})
        funded = stats.get("funded_txo_sum", 0)
        spent = stats.get("spent_txo_sum", 0)
        satoshis = funded - spent
        return satoshis / 10 ** chain.decimals
