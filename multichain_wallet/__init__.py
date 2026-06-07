"""Multi-chain cryptocurrency wallet balance checker."""

__version__ = "1.0.0"

from multichain_wallet.checker import WalletChecker
from multichain_wallet.chains import CHAINS

__all__ = ["WalletChecker", "CHAINS"]
