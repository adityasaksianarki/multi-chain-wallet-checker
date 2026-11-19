"""Docs-consistency tests: the chain counts claimed in README, the CLI
help text, and pyproject.toml must match the real CHAINS table.

Regression test for the "20+ chains" headline, which was wrong: CHAINS
has 19 entries (17 EVM + 2 non-EVM).
"""

import re
from pathlib import Path

from multichain_wallet.chains import CHAINS

ROOT = Path(__file__).resolve().parent.parent


def _evm_count() -> int:
    return sum(1 for c in CHAINS.values() if c.is_evm)


def test_readme_headline_count_matches_chains():
    readme = (ROOT / "README.md").read_text()
    assert f"{len(CHAINS)} blockchains" in readme
    assert "20+" not in readme


def test_readme_chain_table_matches_chains():
    readme = (ROOT / "README.md").read_text()
    rows = re.findall(r"^\| ([^|]+) \| ([A-Za-z0-9]+) \| (EVM|Non-EVM) \|$", readme, re.M)
    assert len(rows) == len(CHAINS), f"table has {len(rows)} rows, CHAINS has {len(CHAINS)}"
    chain_names = [c.name for c in CHAINS.values()]
    for table_name, symbol, kind in rows:
        # Table uses short forms ("Arbitrum", "Avalanche"); accept either
        # direction of substring match against the canonical CHAINS names.
        assert any(
            table_name in name or name in table_name for name in chain_names
        ), f"{table_name!r} not in CHAINS"
        match = next(c for c in CHAINS.values() if table_name in c.name or c.name in table_name)
        assert match.symbol == symbol
        assert ("EVM" if match.is_evm else "Non-EVM") == kind


def test_cli_description_count_matches_chains():
    cli_src = (ROOT / "multichain_wallet" / "cli.py").read_text()
    assert f"across {len(CHAINS)} chains" in cli_src
    assert "20+" not in cli_src


def test_pyproject_description_evm_count_matches_chains():
    pyproject = (ROOT / "pyproject.toml").read_text()
    assert f"{_evm_count()} EVM chains" in pyproject
    assert "20+" not in pyproject


def test_pyproject_license_is_spdx_string():
    """`license = {text = "MIT"}` triggers a setuptools 84 deprecation
    warning (and breaks builds by 2027-02-18); the SPDX string form
    `license = "MIT"` needs setuptools>=77, and the MIT classifier is
    likewise deprecated once the SPDX expression is used."""
    pyproject = (ROOT / "pyproject.toml").read_text()
    assert re.search(r'^license = "MIT"$', pyproject, re.M)
    assert "License ::" not in pyproject
    match = re.search(r'^requires = \["setuptools>=(\d+)', pyproject, re.M)
    assert match and int(match.group(1)) >= 77
