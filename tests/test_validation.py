"""Tests for multichain_wallet.validation — no network access needed."""

import pytest

from multichain_wallet.validation import (
    is_bitcoin_address,
    is_evm_address,
    is_solana_address,
    validate_address,
)

# Addresses from the project README / well-known test vectors.
EVM_VALID = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
EVM_VALID_LOWER = "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
SOL_VALID = "5FHwkrdxntdK24hgQU8qgBjn35Y1zwhz1GZwCNA9yoCr"
BTC_LEGACY_VALID = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"  # genesis address
BTC_BECH32_VALID = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"  # BIP-173 vector


class TestEvm:
    def test_valid_checksummed(self):
        assert is_evm_address(EVM_VALID)

    def test_valid_lowercase(self):
        assert is_evm_address(EVM_VALID_LOWER)

    def test_missing_prefix(self):
        assert not is_evm_address("d8dA6BF26964aF9D7eEd9e03E53415D37aA96045")

    def test_too_short(self):
        assert not is_evm_address("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96")

    def test_bad_chars(self):
        assert not is_evm_address("0xZZdA6BF26964aF9D7eEd9e03E53415D37aA96045")

    def test_empty_and_none(self):
        assert not is_evm_address("")
        assert not is_evm_address(None)


class TestSolana:
    def test_valid(self):
        assert is_solana_address(SOL_VALID)

    def test_bad_char_zero(self):
        assert not is_solana_address("5FHwkrdxntdK24hgQU8qgBjn35Y1zwhz1GZwCNA9yoC0")

    def test_too_short(self):
        assert not is_solana_address("5FHwkrdxntdK24hgQU8qgBjn35Y1zwhz1GZwCNA9")

    def test_empty(self):
        assert not is_solana_address("")


class TestBitcoin:
    def test_legacy_valid(self):
        assert is_bitcoin_address(BTC_LEGACY_VALID)

    def test_legacy_bad_checksum(self):
        # last char flipped: checksum no longer verifies
        assert not is_bitcoin_address("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNb")

    def test_bech32_valid(self):
        assert is_bitcoin_address(BTC_BECH32_VALID)

    def test_bech32_bad_checksum(self):
        assert not is_bitcoin_address("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlx")

    def test_bech32_wrong_hrp(self):
        assert not is_bitcoin_address("tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")

    def test_garbage(self):
        assert not is_bitcoin_address("not-a-bitcoin-address")
        assert not is_bitcoin_address("")


class TestValidateAddress:
    def test_evm_ok_for_evm_chains(self):
        assert validate_address(EVM_VALID, ["ethereum", "base"])

    def test_evm_rejected_for_solana_only(self):
        with pytest.raises(ValueError, match="Invalid wallet address"):
            validate_address(EVM_VALID, ["solana"])

    def test_solana_ok_for_solana(self):
        assert validate_address(SOL_VALID, ["solana"])

    def test_btc_ok_for_bitcoin(self):
        assert validate_address(BTC_BECH32_VALID, ["bitcoin"])

    def test_garbage_rejected_for_all_chains(self):
        with pytest.raises(ValueError, match="Invalid wallet address"):
            validate_address("hello-world", ["ethereum", "solana", "bitcoin"])

    def test_mixed_selection_accepts_either_format(self):
        assert validate_address(SOL_VALID, ["ethereum", "solana"])
        assert validate_address(EVM_VALID, ["ethereum", "solana"])
