"""Partition pack, RIP and index segment views. Probe uses this; please reuse it."""

from __future__ import annotations

import struct
from dataclasses import dataclass

from .klv import KEY_INDEX_SEGMENT, KEY_RIP, Packet, is_partition, partition_kind


@dataclass
class PartitionPack:
    kind: str
    major: int
    minor: int
    kag: int
    this_partition: int
    previous_partition: int
    footer_partition: int
    header_byte_count: int
    index_byte_count: int
    index_sid: int
    body_offset: int
    body_sid: int
    offset: int


def parse_partition(pkt: Packet) -> PartitionPack:
    # Value layout (this subset, all big-endian):
    # 2 major, 2 minor, 4 KAGSize, 8 ThisPartition, 8 PreviousPartition,
    # 8 FooterPartition, 8 HeaderByteCount, 8 IndexByteCount, 4 IndexSID,
    # 8 BodyOffset, 4 BodySID
    v = pkt.value
    if len(v) < 64:
        raise ValueError(f"partition pack too short at {pkt.offset}")
    major, minor, kag = struct.unpack_from(">HHI", v, 0)
    this_p, prev_p, foot_p, hdr_b, idx_b = struct.unpack_from(">QQQQQ", v, 8)
    index_sid = struct.unpack_from(">I", v, 48)[0]
    body_off, body_sid = struct.unpack_from(">QI", v, 52)
    return PartitionPack(
        kind=partition_kind(pkt.key),
        major=major,
        minor=minor,
        kag=kag,
        this_partition=this_p,
        previous_partition=prev_p,
        footer_partition=foot_p,
        header_byte_count=hdr_b,
        index_byte_count=idx_b,
        index_sid=index_sid,
        body_offset=body_off,
        body_sid=body_sid,
        offset=pkt.offset,
    )


@dataclass
class RipEntry:
    body_sid: int
    partition_offset: int


@dataclass
class Rip:
    entries: list[RipEntry]
    overall_len: int
    offset: int


def parse_rip(pkt: Packet) -> Rip:
    # entries: repeated (4 BodySID + 8 ByteOffset), then 4-byte length of the RIP pack (including key+ber+value)
    v = pkt.value
    if len(v) < 4:
        raise ValueError("RIP too short")
    overall = int.from_bytes(v[-4:], "big")
    rest = v[:-4]
    entries = []
    pos = 0
    while pos + 12 <= len(rest):
        sid = int.from_bytes(rest[pos : pos + 4], "big")
        off = int.from_bytes(rest[pos + 4 : pos + 12], "big")
        entries.append(RipEntry(sid, off))
        pos += 12
    return Rip(entries, overall, pkt.offset)


@dataclass
class IndexSegment:
    index_sid: int
    body_sid: int
    edit_rate_num: int
    edit_rate_den: int
    start_position: int
    duration: int
    edit_unit_byte_counts: list[int]
    offset: int


def parse_index(pkt: Packet) -> IndexSegment:
    # subset: 4 index_sid, 4 body_sid, 4+4 edit rate, 8 start, 8 duration, 4 count, then count*4 byte counts
    v = pkt.value
    if len(v) < 36:
        raise ValueError("index segment too short")
    index_sid, body_sid, en, ed = struct.unpack_from(">IIII", v, 0)
    start, dur, count = struct.unpack_from(">QQI", v, 16)
    counts = []
    pos = 36
    for _ in range(count):
        if pos + 4 > len(v):
            break
        counts.append(int.from_bytes(v[pos : pos + 4], "big"))
        pos += 4
    return IndexSegment(index_sid, body_sid, en, ed, start, dur, counts, pkt.offset)


def classify(pkt: Packet) -> str:
    if is_partition(pkt.key):
        return "partition:" + partition_kind(pkt.key)
    if pkt.key == KEY_RIP:
        return "rip"
    if pkt.key == KEY_INDEX_SEGMENT:
        return "index"
    from .klv import KEY_ESSENCE_CHUNK, KEY_FILL
    if pkt.key == KEY_ESSENCE_CHUNK:
        return "essence"
    if pkt.key == KEY_FILL:
        return "fill"
    return "other"
