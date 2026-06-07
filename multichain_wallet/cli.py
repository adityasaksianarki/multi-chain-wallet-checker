"""CLI entry point — `multichain` command."""

from __future__ import annotations

import argparse
import json
import sys

from multichain_wallet import __version__
from multichain_wallet.checker import WalletChecker
from multichain_wallet.chains import CHAINS


def _format_table(summary) -> str:
    lines = []
    lines.append(f"Wallet: {summary.address}")
    lines.append(f"Chains checked: {summary.total_chains_checked} | Errors: {summary.errors}")
    lines.append("─" * 65)

    has_balance = False
    for r in summary.non_zero:
        has_balance = True
        lines.append(f"  ✅ {r.chain:<20} {r.balance:>14.6f} {r.symbol}")
        lines.append(f"     {r.explorer_url}")

    if not has_balance:
        lines.append("  (no balances found)")

    # Show errors
    errors = [r for r in summary.results if r.error]
    if errors:
        lines.append("─" * 65)
        lines.append("Errors:")
        for r in errors:
            lines.append(f"  ⚠️  {r.chain}: {r.error}")

    return "\n".join(lines)


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        prog="multichain",
        description="Check crypto wallet balances across 20+ chains.",
    )
    parser.add_argument("address", help="Wallet address (EVM 0x... or Solana/BTC)")
    parser.add_argument(
        "-c", "--chains", nargs="*", default=None,
        help=f"Chains to check (default: all). Options: {', '.join(CHAINS.keys())}",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output as JSON")
    parser.add_argument("--workers", type=int, default=8, help="Max parallel workers (default: 8)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args(argv)

    try:
        checker = WalletChecker(chains=args.chains, timeout=15)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Checking {args.address} across {len(checker.chains)} chains...", file=sys.stderr)
    summary = checker.check_all(args.address, max_workers=args.workers)

    if args.as_json:
        output = {
            "address": summary.address,
            "total_checked": summary.total_chains_checked,
            "errors": summary.errors,
            "balances": [
                {
                    "chain": r.chain, "symbol": r.symbol,
                    "balance": r.balance, "explorer": r.explorer_url,
                    "error": r.error,
                }
                for r in summary.results
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(_format_table(summary))


if __name__ == "__main__":
    main()
