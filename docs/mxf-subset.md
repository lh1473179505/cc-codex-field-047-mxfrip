# 本仓库使用的 OP1a 子集

这不是完整的 SMPTE ST 377 MXF。只处理下列 16 字节键（十六进制）：

| 键 | 含义 |
|---|---|
| 06 0e 2b 34 02 05 01 01 0d 01 02 01 01 02 01 02 | Header Partition Pack |
| 06 0e 2b 34 02 05 01 01 0d 01 02 01 01 02 02 03 | Body Partition Pack |
| 06 0e 2b 34 02 05 01 01 0d 01 02 01 01 02 03 04 | Footer Partition Pack |
| 06 0e 2b 34 02 53 01 01 0d 01 02 01 01 10 01 00 | Index Table Segment（简化） |
| 06 0e 2b 34 02 05 01 01 0d 01 02 01 01 11 01 00 | Random Index Pack |
| 06 0e 2b 34 01 02 01 01 0d 01 03 01 16 01 00 00 | Essence 数据块（夹具用的裸 PCM 块） |
| 06 0e 2b 34 01 01 01 01 02 04 10 03 00 00 00 00 | KLV Fill |

长度是 BER（短形式或长形式，禁止 indefinite）。KAG 默认 512。Fill 用于把下一包的起始对齐到 KAG 倍数。

## Partition Pack 值（大端）

`major:u16, minor:u16, KAGSize:u32, ThisPartition:u64, PreviousPartition:u64, FooterPartition:u64, HeaderByteCount:u64, IndexByteCount:u64, IndexSID:u32, BodyOffset:u64, BodySID:u32`

`ThisPartition` / `PreviousPartition` / `FooterPartition` 是相对文件开头的绝对字节偏移。`HeaderByteCount` 是头分区里分区包之后、第一个 essence 之前的字节数。`IndexByteCount` 是本分区携带的 Index 段（含 Fill）字节数。

## Index Table Segment 值（大端，简化）

`IndexSID:u32, BodySID:u32, EditRateNum:u32, EditRateDen:u32, StartPosition:u64, Duration:u64, Count:u32, then Count 个 u32 EditUnitByteCount`

每个 EditUnitByteCount 对应一个编辑单元（夹具里就是一块 essence 包的全部 KLV 大小，含 key+BER+value）。

## RIP 值

重复 `BodySID:u32 + ByteOffset:u64`，最后 4 字节是整个 RIP 包的长度（含 key、BER 和 value）。RIP 必须是文件的最后一个包，并且紧跟在 Footer 分区之后。
