"""KLV / BER helpers and well-known Operational Pattern 1a keys. Probe uses this; please reuse it."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# 16-byte Universal Labels used by this subset. See docs/mxf-subset.md.
KEY_PARTITION_PACK = bytes.fromhex("060e2b34020501010d01020101020000")  # last two bytes overwritten per kind
# We store kind in the last two bytes:
#  01 02 header open incomplete
#  02 03 body closed incomplete  (used loosely)
#  03 04 footer closed complete
# To keep parsing simple, KEY prefix (14 bytes) identifies a partition pack, last two bytes are kind.

PARTITION_PREFIX = bytes.fromhex("060e2b34020501010d0102010102")
KEY_RIP = bytes.fromhex("060e2b34020501010d01020101110100")
KEY_INDEX_SEGMENT = bytes.fromhex("060e2b34025301010d01020101100100")
KEY_ESSENCE_CHUNK = bytes.fromhex("060e2b34010201010d01030116010000")  # generic sound/data chunk used by fixtures
KEY_FILL = bytes.fromhex("060e2b34010101010204100300000000")


class KlvError(ValueError):
    pass


def encode_ber(length: int) -> bytes:
    if length < 128:
        return bytes([length])
    # long form
    n = (length.bit_length() + 7) // 8
    return bytes([0x80 | n]) + length.to_bytes(n, "big")


def decode_ber(data: bytes, offset: int = 0) -> tuple[int, int]:
    """Return (length, new_offset)."""
    if offset >= len(data):
        raise KlvError("truncated BER")
    b = data[offset]
    if b < 128:
        return b, offset + 1
    n = b & 0x7F
    if n == 0:
        raise KlvError("indefinite BER is not allowed in this subset")
    if offset + 1 + n > len(data):
        raise KlvError("truncated long BER")
    length = int.from_bytes(data[offset + 1 : offset + 1 + n], "big")
    return length, offset + 1 + n


@dataclass
class Packet:
    key: bytes
    length: int
    value: bytes
    offset: int  # start of the key
    end: int     # first byte after the value


def iter_klv(blob: bytes) -> list[Packet]:
    out: list[Packet] = []
    pos = 0
    while pos + 16 <= len(blob):
        key = blob[pos : pos + 16]
        try:
            length, voff = decode_ber(blob, pos + 16)
        except KlvError:
            break
        end = voff + length
        if end > len(blob):
            # truncated last packet: still emit with short value
            out.append(Packet(key, length, blob[voff:], pos, len(blob)))
            break
        out.append(Packet(key, length, blob[voff:end], pos, end))
        pos = end
        # KAG alignment is handled by FILL packets, no implicit skip
    return out


def read_klv(path: str) -> list[Packet]:
    return iter_klv(Path(path).read_bytes())


def is_partition(key: bytes) -> bool:
    return key[:14] == PARTITION_PREFIX


def partition_kind(key: bytes) -> str:
    last = key[14:16]
    return {b"\x01\x02": "header", b"\x02\x03": "body", b"\x03\x04": "footer"}.get(last, "partition")
