from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import probe, repair


def cmd_probe(args: argparse.Namespace) -> int:
    info = probe.probe_path(args.input)
    text = probe.format_probe(info)
    if args.out:
        Path(args.out).write_text(text + "\n")
    else:
        sys.stdout.write(text + "\n")
    return 0


def cmd_repair(args: argparse.Namespace) -> int:
    try:
        return repair.repair(args.input, args.output, args.policy, args.report)
    except repair.NotImplementedRepair as e:
        sys.stderr.write(str(e) + "\n")
        return 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mxfrip")
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("probe", help="inventory a subset OP1a file")
    sp.add_argument("--input", required=True)
    sp.add_argument("--out", default=None)
    sp.set_defaults(func=cmd_probe)
    sr = sub.add_parser("repair", help="rebuild index, RIP and partition offsets")
    sr.add_argument("--input", required=True)
    sr.add_argument("--output", required=True)
    sr.add_argument("--policy", required=True)
    sr.add_argument("--report", required=True)
    sr.set_defaults(func=cmd_repair)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
