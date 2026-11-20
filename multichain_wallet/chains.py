"""Chain configuration — RPC endpoints and native token metadata."""

from dataclasses import dataclass


@dataclass
class Chain:
    chain_id: int
    name: str
    symbol: str
    rpc_url: str
    explorer: str
    decimals: int = 18
    is_evm: bool = True


# ── Public RPC endpoints (no key required) ──────────────────────────────
# These are rate-limited public endpoints. For production use, get a free
# key from Alchemy, Infura, or QuickNode and override via env vars.

CHAINS: dict[str, Chain] = {
    # EVM chains
    "ethereum": Chain(
        chain_id=1, name="Ethereum", symbol="ETH",
        rpc_url="https://eth.llamarpc.com",
        explorer="https://etherscan.io",
    ),
    "bsc": Chain(
        chain_id=56, name="BNB Smart Chain", symbol="BNB",
        rpc_url="https://bsc-dataseed1.binance.org",
        explorer="https://bscscan.com",
    ),
    "polygon": Chain(
        chain_id=137, name="Polygon", symbol="POL",
        rpc_url="https://polygon-rpc.com",
        explorer="https://polygonscan.com",
    ),
    "arbitrum": Chain(
        chain_id=42161, name="Arbitrum One", symbol="ETH",
        rpc_url="https://arb1.arbitrum.io/rpc",
        explorer="https://arbiscan.io",
    ),
    "optimism": Chain(
        chain_id=10, name="Optimism", symbol="ETH",
        rpc_url="https://mainnet.optimism.io",
        explorer="https://optimistic.etherscan.io",
    ),
    "base": Chain(
        chain_id=8453, name="Base", symbol="ETH",
        rpc_url="https://mainnet.base.org",
        explorer="https://basescan.org",
    ),
    "avalanche": Chain(
        chain_id=43114, name="Avalanche C-Chain", symbol="AVAX",
        rpc_url="https://api.avax.network/ext/bc/C/rpc",
        explorer="https://snowtrace.io",
        decimals=18,
    ),
    "fantom": Chain(
        chain_id=250, name="Fantom", symbol="FTM",
        rpc_url="https://rpc.ftm.tools",
        explorer="https://ftmscan.com",
    ),
    "linea": Chain(
        chain_id=59144, name="Linea", symbol="ETH",
        rpc_url="https://rpc.linea.build",
        explorer="https://lineascan.build",
    ),
    "scroll": Chain(
        chain_id=534352, name="Scroll", symbol="ETH",
        rpc_url="https://rpc.scroll.io",
        explorer="https://scrollscan.com",
    ),
    "zksync": Chain(
        chain_id=324, name="zkSync Era", symbol="ETH",
        rpc_url="https://mainnet.era.zksync.io",
        explorer="https://explorer.zksync.io",
    ),
    "blast": Chain(
        chain_id=81457, name="Blast", symbol="ETH",
        rpc_url="https://rpc.blast.io",
        explorer="https://blastscan.io",
    ),
    "manta": Chain(
        chain_id=169, name="Manta Pacific", symbol="ETH",
        rpc_url="https://pacific-rpc.manta.network/http",
        explorer="https://pacific-explorer.manta.network",
    ),
    "mantle": Chain(
        chain_id=5000, name="Mantle", symbol="MNT",
        rpc_url="https://rpc.mantle.xyz",
        explorer="https://mantlescan.xyz",
    ),
    "celo": Chain(
        chain_id=42220, name="Celo", symbol="CELO",
        rpc_url="https://forno.celo.org",
        explorer="https://celoscan.io",
    ),
    "gnosis": Chain(
        chain_id=100, name="Gnosis", symbol="xDAI",
        rpc_url="https://rpc.gnosis.gateway.fm",
        explorer="https://gnosisscan.io",
    ),
    "cronos": Chain(
        chain_id=25, name="Cronos", symbol="CRO",
        rpc_url="https://evm.cronos.org",
        explorer="https://cronoscan.com",
    ),
    "elysium": Chain(
        chain_id=99901, name="Elysium", symbol="HYPE",
        rpc_url="https://rpc.elysium.kinetiq.xyz",
        explorer="https://elysium.kinetiq.xyz/explorer",
    ),
    # Non-EVM
    "solana": Chain(
        chain_id=0, name="Solana", symbol="SOL",
        rpc_url="https://api.mainnet-beta.solana.com",
        explorer="https://solscan.io",
        decimals=9,
        is_evm=False,
    ),
    "bitcoin": Chain(
        chain_id=0, name="Bitcoin", symbol="BTC",
        rpc_url="https://blockstream.info/api",
        explorer="https://blockstream.info",
        decimals=8,
        is_evm=False,
    ),
}
