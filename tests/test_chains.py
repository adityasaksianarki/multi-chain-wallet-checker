"""Chain-table tests: the Elysium entry (chain id 99901) must carry the
official Kinetiq parameters, verified live against the public RPC on
2026-11-20: eth_chainId returned 0x1863d (99901), eth_getBalance on a
known address returned a valid result.
"""

from multichain_wallet.chains import CHAINS


def test_elysium_chain_entry():
    elysium = CHAINS["elysium"]
    assert elysium.chain_id == 99901
    assert elysium.name == "Elysium"
    assert elysium.symbol == "HYPE"
    assert elysium.rpc_url == "https://rpc.elysium.kinetiq.xyz"
    assert elysium.explorer == "https://elysium.kinetiq.xyz/explorer"
    assert elysium.decimals == 18
    assert elysium.is_evm is True


def test_elysium_chain_id_is_unique():
    ids = [c.chain_id for c in CHAINS.values() if c.is_evm]
    assert ids.count(99901) == 1
