# 数据包说明

数据随本 private 仓分发，**仅限仓内协作者使用，禁止外传或转存公开渠道**。

## 当前数据包（随 TASK-001 发放）

| 文件 | 内容 | 说明 |
|---|---|---|
| `panel_monthly.csv.gz` | 月度面板 | 列: date(月末), code, close, ret_fwd20(未来20交易日收益, 标签), bench_ret_fwd20(基准同期收益) |
| `events_sample.csv` | 样例事件清单 | 列: date, code, event_type |

数据纪律：
- 面板已做 PIT（point-in-time）处理，禁止自行拼接未来数据
- 衍生中间产物放 data/ 下，大文件(*.parquet/*.pkl)仍不入库