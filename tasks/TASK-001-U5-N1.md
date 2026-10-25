# TASK-001 · 事件研究 + 多重检验模块（U5/N1）

- **状态**：待领取
- **预计产出**：`framework/evaluation.py` 全部函数实现 + 测试 + 研究报告
- **前置**：读完本工单，先交一页纸预注册方案（假设/门槛/证伪条件）

## 背景

研究管线需要两个通用统计工具：
1. **事件研究**：给定事件清单（日期+代码），统计事件后 1/2/5/10 个交易日的累计超额收益及显著性
2. **BH-FDR 多重检验**：批量因子/策略检验时控制假发现率

## 接口契约

实现 `framework/evaluation.py` 中全部 5 个函数，签名与 docstring 为准，不得改动签名。

## 验收标准（全部满足才算完成）

1. **正确性**
   - `bh_fdr` 输出与 `statsmodels.stats.multitest.multipletests(method="fdr_bh")` 逐点一致（随机 1000 组 p 值测试）
   - `rank_ic` 与 `scipy.stats.spearmanr` 一致
   - `event_study` 用**构造数据**验证：面板中给事件股注入已知 +2%/日 的漂移，要求估计出的 mean_excess 在 ±0.1% 内
2. **稳健性**
   - 事件日后数据不足窗口长度时，该事件剔除并在报告中计数
   - 有效样本 < 10 时 rank_ic 返回 NaN 而不报错
   - 输入含 NaN 时自动剔除对应样本
3. **测试**：pytest 全绿，覆盖率包含上述全部边界
4. **研究报告**（`reports/TASK-001-report.md`）
   - 用分发的 `panel_monthly.parquet` + `events_sample.csv` 跑一遍完整演示
   - 输出事件研究表 + 一段结论（超额是否显著、哪个窗口最强）
   - 贴 BH-FDR 与 Bonferroni 在同一组 p 值上的拒绝数对比

## 数据

见 `data/README.md`。数据随任务单独发放，不入库。

## 禁止事项

- 不得修改接口签名
- 不得引入 requirements.txt 之外的依赖（确需新增先在 PR 里说明理由）
- 不得在代码中硬编码任何绝对路径
