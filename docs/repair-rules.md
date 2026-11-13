# repair 规则

默认策略见 `fixtures/policy.json`。

## 目标

读入一份可能残缺的子集 OP1a 文件，写出一份新文件，使：

1. 存在 Header、至少一个 Body（若输入里已有 essence）、Footer。
2. 每个分区包的 This / Previous / Footer 偏移与真实位置一致。FooterPartition 在所有分区包里都指向 Footer 的起始。
3. 每个带 essence 的分区都有正确的 Index Table Segment：`EditUnitByteCount` 与实际 essence KLV 包大小一致，`Duration` 等于单元个数，`StartPosition` 从 0 连续累计。
4. 文件以 RIP 结束，条目覆盖全部分区（Header 的 BodySID 为 0），ByteOffset 正确，末尾 4 字节长度等于整个 RIP KLV 的大小。
5. KAG 按策略 `kag`（默认 512）补 Fill，Fill 不得跨越分区界限。

## 夹具

- `fixtures/truncated.mxf`：有 Header 和 Body essence，但没有 Footer，也没有 RIP。Index 缺失。
- `fixtures/stale-index.mxf`：有 Footer 和 RIP，但 RIP 里的偏移是错的，Index 的 byte count 还是按更早一次写入留下的旧值，和现在的 essence 对不上。

## 退出码

- 成功写出可被本仓库 `probe` 解析、且满足上面 5 条的文件和完整报告：退出 0，`decision` 为 `ok`。
- 输入里没有任何 essence，无法重建：退出 1，`decision` 为 `reject`，`reason_codes` 含 `no_essence`。
- 文件完全无法按 KLV 扫描：退出 2。
