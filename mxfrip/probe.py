"""Read-only inventory of a subset OP1a MXF file."""

from __future__ import annotations

import json

from . import klv, partition


def probe_path(path: str) -> dict:
    blob_packets = klv.read_klv(path)
    parts = []
    rips = []
    indexes = []
    essence = 0
    fills = 0
    others = 0
    truncated = False
    for pkt in blob_packets:
        kind = partition.classify(pkt)
        if pkt.end - pkt.offset < 16 + 1 + pkt.length:
            truncated = True
        if kind.startswith("partition:"):
            pp = partition.parse_partition(pkt)
            parts.append(
                {
                    "kind": pp.kind,
                    "offset": pp.offset,
                    "this_partition": pp.this_partition,
                    "previous_partition": pp.previous_partition,
                    "footer_partition": pp.footer_partition,
                    "kag": pp.kag,
                    "index_byte_count": pp.index_byte_count,
                    "index_sid": pp.index_sid,
                    "body_sid": pp.body_sid,
                    "body_offset": pp.body_offset,
                }
            )
        elif kind == "rip":
            rip = partition.parse_rip(pkt)
            rips.append(
                {
                    "offset": rip.offset,
                    "overall_len": rip.overall_len,
                    "entries": [{"body_sid": e.body_sid, "partition_offset": e.partition_offset} for e in rip.entries],
                }
            )
        elif kind == "index":
            idx = partition.parse_index(pkt)
            indexes.append(
                {
                    "offset": idx.offset,
                    "index_sid": idx.index_sid,
                    "body_sid": idx.body_sid,
                    "edit_rate": [idx.edit_rate_num, idx.edit_rate_den],
                    "start_position": idx.start_position,
                    "duration": idx.duration,
                    "units": len(idx.edit_unit_byte_counts),
                    "byte_count_sum": sum(idx.edit_unit_byte_counts),
                }
            )
        elif kind == "essence":
            essence += 1
        elif kind == "fill":
            fills += 1
        else:
            others += 1
    return {
        "path": path,
        "packets": len(blob_packets),
        "truncated_klv": truncated,
        "partitions": parts,
        "rips": rips,
        "indexes": indexes,
        "essence_chunks": essence,
        "fills": fills,
        "others": others,
    }


def format_probe(info: dict) -> str:
    return json.dumps(info, ensure_ascii=False, indent=2)
