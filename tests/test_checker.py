"""Checker tests with mocked Web3/requests — no network access.

Covers the Day 6 backlog item:
- single-chain check (EVM, Solana, Bitcoin) returns the mocked balance
- unknown chain returns an error result instead of raising
- RPC failure (unreachable EVM node, RPC-level error, HTTP failure)
  surfaces as an error result on that chain
- invalid address raises ValueError up front (fail fast)
- check_all counts errors and reports per-chain results
"""

import requests
import pytest

from multichain_wallet import checker as checker_mod
from multichain_wallet.checker import WalletChecker

EVM_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
SOL_ADDRESS = "FoWN9yPBEM69ouGyEuBVJ9xRfwppcoip7ZaoGtuPBHgK"
BTC_ADDRESS = "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"


# ── Fakes ────────────────────────────────────────────────────────────────

class _FakeEth:
    def __init__(self, wei, exc=None):
        self._wei = wei
        self._exc = exc

    def get_balance(self, _address):
        if self._exc is not None:
            raise self._exc
        return self._wei


class FakeWeb3:
    """Stand-in for web3.Web3 with class-level knobs per test."""

    connected = True
    wei = 1_500_000_000_000_000_000  # 1.5 ETH
    exc = None

    def __init__(self, _provider):
        self.eth = _FakeEth(FakeWeb3.wei, FakeWeb3.exc)

    @staticmethod
    def HTTPProvider(_url, request_kwargs=None):
        return ("provider", _url, request_kwargs)

    def is_connected(self):
        return FakeWeb3.connected

    @staticmethod
    def to_checksum_address(address):
        return address

    @staticmethod
    def from_wei(value, _unit):
        return value / 10**18


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload



@pytest.fixture(autouse=True)
def _patch_web3(monkeypatch):
    monkeypatch.setattr(checker_mod, "Web3", FakeWeb3)
    FakeWeb3.connected = True
    FakeWeb3.wei = 1_500_000_000_000_000_000
    FakeWeb3.exc = None


# ── EVM ──────────────────────────────────────────────────────────────────

def test_check_evm_chain_returns_mocked_balance():
    result = WalletChecker(chains=["ethereum"]).check(EVM_ADDRESS, "ethereum")
    assert result.error is None
    assert result.balance == pytest.approx(1.5)
    assert result.symbol == "ETH"
    assert result.chain == "Ethereum"
    assert result.explorer_url.endswith(f"/address/{EVM_ADDRESS}")


def test_check_evm_rpc_unreachable_returns_error_result():
    FakeWeb3.connected = False
    result = WalletChecker(chains=["ethereum"]).check(EVM_ADDRESS, "ethereum")
    assert result.balance == 0
    assert result.error is not None
    assert "Cannot connect" in result.error


def test_check_evm_get_balance_raises_returns_error_result():
    FakeWeb3.exc = RuntimeError("boom")
    result = WalletChecker(chains=["ethereum"]).check(EVM_ADDRESS, "ethereum")
    assert result.balance == 0
    assert result.error == "boom"


# ── Solana ───────────────────────────────────────────────────────────────

def test_check_solana_returns_mocked_balance(monkeypatch):
    def fake_post(_url, json=None, timeout=None):
        assert json["method"] == "getBalance"
        assert json["params"] == [SOL_ADDRESS]
        return FakeResponse({"result": {"value": 2_500_000_000}})

    monkeypatch.setattr(checker_mod.requests, "post", fake_post)
    result = WalletChecker(chains=["solana"]).check(SOL_ADDRESS, "solana")
    assert result.error is None
    assert result.balance == pytest.approx(2.5)
    assert result.symbol == "SOL"


def test_check_solana_rpc_error_returns_error_result(monkeypatch):
    def fake_post(_url, json=None, timeout=None):
        return FakeResponse({"error": {"message": "Invalid param: address"}})

    monkeypatch.setattr(checker_mod.requests, "post", fake_post)
    result = WalletChecker(chains=["solana"]).check(SOL_ADDRESS, "solana")
    assert result.balance == 0
    assert result.error == "Invalid param: address"


# ── Bitcoin ──────────────────────────────────────────────────────────────

def test_check_bitcoin_returns_mocked_balance(monkeypatch):
    def fake_get(url, timeout=None):
        assert url.endswith(f"/address/{BTC_ADDRESS}")
        return FakeResponse({
            "chain_stats": {"funded_txo_sum": 100_000_000, "spent_txo_sum": 50_000_000},
            "mempool_stats": {"funded_txo_sum": 0, "spent_txo_sum": 0},
        })

    monkeypatch.setattr(checker_mod.requests, "get", fake_get)
    result = WalletChecker(chains=["bitcoin"]).check(BTC_ADDRESS, "bitcoin")
    assert result.error is None
    assert result.balance == pytest.approx(0.5)
    assert result.symbol == "BTC"


def test_check_bitcoin_http_failure_returns_error_result(monkeypatch):
    def fake_get(_url, timeout=None):
        return FakeResponse({}, status=503)

    monkeypatch.setattr(checker_mod.requests, "get", fake_get)
    result = WalletChecker(chains=["bitcoin"]).check(BTC_ADDRESS, "bitcoin")
    assert result.balance == 0
    assert "503" in result.error


# ── Unknown chain / validation / summary ─────────────────────────────────

def test_check_unknown_chain_returns_error_result():
    result = WalletChecker(chains=["ethereum"]).check(EVM_ADDRESS, "notachain")
    assert result.balance == 0
    assert result.error == "Unknown chain: notachain"


def test_unknown_chain_in_constructor_raises():
    with pytest.raises(ValueError, match="Unknown chains"):
        WalletChecker(chains=["ethereum", "notachain"])


def test_check_invalid_address_raises_value_error():
    with pytest.raises(ValueError, match="Invalid wallet address"):
        WalletChecker(chains=["ethereum"]).check("not-an-address", "ethereum")


def test_check_all_counts_errors_and_sorts_results(monkeypatch):
    # Ethereum succeeds (mocked), Solana fails (RPC error) — one error total.
    def fake_post(_url, json=None, timeout=None):
        return FakeResponse({"error": {"message": "node down"}})

    monkeypatch.setattr(checker_mod.requests, "post", fake_post)
    summary = WalletChecker(chains=["ethereum", "solana"]).check_all(EVM_ADDRESS)
    assert summary.total_chains_checked == 2
    assert summary.errors == 1
    assert [r.chain for r in summary.results] == ["Ethereum", "Solana"]
    assert summary.non_zero == [r for r in summary.results if r.chain == "Ethereum"]


def test_check_all_invalid_address_raises_before_any_rpc():
    with pytest.raises(ValueError, match="Invalid wallet address"):
        WalletChecker(chains=["ethereum"]).check_all("not-an-address")
