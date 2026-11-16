"""Wallet address validation — fail fast on typos instead of fanning out
to every chain RPC and collecting one error per chain.

Supported formats:
- EVM: 0x-prefixed 40 hex chars (any case), via web3's checksum-aware check.
- Solana: base58 string decoding to exactly 32 bytes.
- Bitcoin: legacy base58check (1.../3...) or bech32/bech32m (bc1q.../bc1p...)
  with full checksum verification (BIP-173 / BIP-350).
"""

from __future__ import annotations

import hashlib

import base58
from web3 import Web3

from multichain_wallet.chains import CHAINS

__all__ = [
    "is_evm_address",
    "is_solana_address",
    "is_bitcoin_address",
    "validate_address",
]


def is_evm_address(address: str) -> bool:
    """True for a 0x-prefixed 40-hex-char address (any case).

    The 0x prefix is required: every documented input format uses it,
    and accepting bare hex would hide a copy-paste slip.
    """
    if not isinstance(address, str):
        return False
    return address.startswith("0x") and Web3.is_address(address)


def is_solana_address(address: str) -> bool:
    """True for a base58 string decoding to exactly 32 bytes."""
    if not isinstance(address, str) or not address:
        return False
    try:
        return len(base58.b58decode(address)) == 32
    except Exception:
        return False


# ── Bitcoin ─────────────────────────────────────────────────────────────

_BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
_BECH32_CONST = 1            # BIP-173 (bc1q...)
_BECH32M_CONST = 0x2BC830A3  # BIP-350 (bc1p...)


def _bech32_polymod(values: list[int]) -> int:
    generator = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ value
        for i in range(5):
            if (top >> i) & 1:
                chk ^= generator[i]
    return chk


def _bech32_hrp_expand(hrp: str) -> list[int]:
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def _is_bech32_address(address: str) -> bool:
    """BIP-173/BIP-350 checksum verification for bc1... addresses."""
    if address != address.lower() and address != address.upper():
        return False  # mixed case is invalid in bech32
    address = address.lower()
    if len(address) > 90 or not address.startswith("bc1"):
        return False
    sep = address.rfind("1")
    hrp, data_part = address[:sep], address[sep + 1:]
    if hrp != "bc" or len(data_part) < 6:
        return False
    try:
        data = [_BECH32_CHARSET.index(c) for c in data_part]
    except ValueError:
        return False
    return _bech32_polymod(_bech32_hrp_expand(hrp) + data) in (
        _BECH32_CONST,
        _BECH32M_CONST,
    )


def _is_base58check_address(address: str) -> bool:
    """Legacy 1.../3... address: 21 bytes (1 version + 20 hash) with a
    valid double-SHA256 checksum."""
    if not address or address[0] not in "13":
        return False
    try:
        return len(base58.b58decode_check(address)) == 21
    except Exception:
        return False


def is_bitcoin_address(address: str) -> bool:
    """True for a legacy base58check or bech32/bech32m Bitcoin address."""
    if not isinstance(address, str) or not address:
        return False
    return _is_base58check_address(address) or _is_bech32_address(address)


# ── Combined check ──────────────────────────────────────────────────────


def validate_address(address: str, chain_names: list[str]) -> bool:
    """Validate ``address`` against the chain types in ``chain_names``.

    Returns True if the address is valid for at least one selected chain
    type. Raises ValueError otherwise, so callers fail fast instead of
    issuing one doomed RPC call per chain.
    """
    names = [c.lower() for c in chain_names]
    selected = [CHAINS[n] for n in names if n in CHAINS]

    tried: list[tuple[str, bool]] = []
    if any(c.is_evm for c in selected):
        tried.append(("EVM", is_evm_address(address)))
    if any(c.name == "Solana" for c in selected):
        tried.append(("Solana", is_solana_address(address)))
    if any(c.name == "Bitcoin" for c in selected):
        tried.append(("Bitcoin", is_bitcoin_address(address)))

    if tried and any(ok for _, ok in tried):
        return True

    formats = ", ".join(name for name, _ in tried) or "any known chain"
    raise ValueError(
        f"Invalid wallet address: {address!r} "
        f"(not a valid {formats} address for the selected chains)"
    )
