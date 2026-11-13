# mxfrip

修理写到一半的 OP1a MXF 的工具。`probe` 已经能按本仓库的子集把 KLV、分区包、Index 和 RIP 列出来。`repair` 还没有实现。

不要引入 bmx、libMXF、ffmpeg-python 或 mxflib，也不要使用 Docker。请复用 `mxfrip.klv` 和 `mxfrip.partition`。键值和字段布局以 `docs/mxf-subset.md` 为准，不要去猜完整 SMPTE 规范里未出现在该文档中的包。

## 命令

```
python -m mxfrip probe --input fixtures/truncated.mxf
python -m mxfrip repair \
  --input fixtures/truncated.mxf \
  --output /tmp/mxfrip-out.mxf \
  --policy fixtures/policy.json \
  --report /tmp/mxfrip-report.json
```

规则见 `docs/repair-rules.md`，报告字段见 `docs/report-schema.md`。
