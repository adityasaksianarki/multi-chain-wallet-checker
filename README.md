# Multi-Chain Wallet Checker

Check cryptocurrency wallet balances across **19 blockchains** in one command.

Supports EVM chains (Ethereum, BSC, Polygon, Arbitrum, Optimism, Base, and 11 more), Solana, and Bitcoin — all with a single CLI tool or Python API.

## Install

```bash
pip install git+https://github.com/adityasaksianarki/multi-chain-wallet-checker.git
```

Or clone and install locally:

```bash
git clone https://github.com/adityasaksianarki/multi-chain-wallet-checker.git
cd multi-chain-wallet-checker
pip install -e .
```

## CLI Usage

```bash
# Check all chains
multichain 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

# Specific chains only
multichain 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 -c ethereum arbitrum base

# JSON output
multichain 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --json

# Solana wallet
multichain 5FHwkrdxntdK24hgQU8qgBjn35Y1zwhz1GZwCNA9yoCr -c solana

# Bitcoin wallet
multichain bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh -c bitcoin
```

## Python API

```python
from multichain_wallet import WalletChecker

checker = WalletChecker()  # all chains
summary = checker.check_all("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")

for r in summary.non_zero:
    print(f"{r.chain}: {r.balance:.6f} {r.symbol}")
```

## Supported Chains

| Chain | Symbol | Type |
|-------|--------|------|
| Ethereum | ETH | EVM |
| BNB Smart Chain | BNB | EVM |
| Polygon | POL | EVM |
| Arbitrum | ETH | EVM |
| Optimism | ETH | EVM |
| Base | ETH | EVM |
| Avalanche | AVAX | EVM |
| Fantom | FTM | EVM |
| Linea | ETH | EVM |
| Scroll | ETH | EVM |
| zkSync Era | ETH | EVM |
| Blast | ETH | EVM |
| Manta Pacific | ETH | EVM |
| Mantle | MNT | EVM |
| Celo | CELO | EVM |
| Gnosis | xDAI | EVM |
| Cronos | CRO | EVM |
| Solana | SOL | Non-EVM |
| Bitcoin | BTC | Non-EVM |

## Custom RPC

Override RPC endpoints via environment variables:

```bash
export ETH_RPC_URL="https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"
export SOL_RPC_URL="https://api.mainnet-beta.solana.com"
```

## License

MIT
