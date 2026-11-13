"""Rebuild Index / RIP / partition offsets for subset OP1a MXF. Not implemented in the initial snapshot."""

from __future__ import annotations


class NotImplementedRepair(NotImplementedError):
    pass


def repair(input_path: str, output_path: str, policy_path: str, report_path: str) -> int:
    raise NotImplementedRepair(
        "mxfrip.repair.repair is not implemented yet; KLV / partition probe already work"
    )
