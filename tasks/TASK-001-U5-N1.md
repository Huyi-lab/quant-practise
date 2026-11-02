# TASK-001 · 事件研究 + 多重检验模块（U5/N1）

- **状态**：待领取

- **预计产出**：`framework/evaluation.py` 全部函数实现 + pytest 测试 + 研究报告

- **前置**：读完本工单，先交一页纸预注册方案（假设/门槛/证伪条件），拍板后才跑实验

***

## 0. 一句话理解这个任务

给你一份 119 个月 × 约 3000 只股票的月度面板数据，实现 5 个统计函数，回答两类问题：

1. **因子类**：某个因子值高的股票，下个月是不是真的涨得更多？（RankIC / ICIR）
2. **事件类**：某类事件发生后的几个月里，事件股票平均跑赢基准多少？显著吗？（event\_study）
3. **多重检验**：当你一次性检验几十个因子/事件时，怎么防止"碰运气碰出来的假阳性"？（bh\_fdr）

***

## 1. 环境准备

```bash
# Python ≥ 3.10
pip install -r requirements.txt   # pandas / numpy / scipy / statsmodels / pytest
```

把离线分发的两个数据文件放进 `data/` 目录（数据不入库，别 commit）：

```
quant-research/
├── framework/evaluation.py   ← 你要实现的 5 个函数（接口已定义，不准改签名）
├── examples/quickstart.py    ← 参考示例：数据→因子→IC 最小闭环，先跑一遍建立直觉
├── tasks/TASK-001-U5-N1.md   ← 本文件
├── data/
│   ├── panel_monthly.csv.gz  ← 主数据（月度面板）
│   └── events_sample.csv     ← 样例事件清单
├── tests/                    ← 你新建的 pytest 测试目录
└── reports/                  ← 你的研究报告放这里
```

**先跑一遍参考示例**，确认环境没问题：

```bash
python examples/quickstart.py
# 期望输出大致：面板: 119 个月度截面, 3269 只标的, IC 均值 : -0.0310 ...
```

***

## 2. 数据长什么样（动手前先看懂数据）

### panel\_monthly.csv.gz（月度面板，约 21 万行）

| date    | code      | close | ret\_fwd20 | bench\_ret\_fwd20 |
| ------- | --------- | ----- | ---------- | ----------------- |
| 2016-01 | 000001.SZ | 10.00 | 0.0400     | 0.0502            |
| 2016-02 | 000001.SZ | 9.56  | 0.0962     | 0.1016            |

列含义：

- `date`：月末标签，格式 `YYYY-MM`（"2016-01" = 2016 年 1 月末这个截面）

- `code`：股票代码

- `close`：该月末收盘价

- `ret_fwd20`：**该行月末之后约 1 个月（20 个交易日）的个股收益**。例：2016-01 行的 0.0400 = 平安银行 2016 年 2 月涨了约 4%

- `bench_ret_fwd20`：基准（市场组合）同期收益

**关键理解（90% 的困惑来自这里）**：

- 每一行 = "某股票在某月末的快照 + 未来 1 个月的表现"

- `date=2016-01` 行的 `ret_fwd20`，就是"2016 年 1 月末 → 2016 年 2 月末"这段的收益

- 数据已做 PIT 处理（只用了当时可得的信息），**禁止自己用未来数据拼标签**，直接用现成的 `ret_fwd20`

### events\_sample.csv（样例事件清单，300 行）

| date    | code      | event\_type |
| ------- | --------- | ----------- |
| 2016-01 | 002073.SZ | policy      |
| 2016-02 | 000828.SZ | policy      |

- `date`：事件发生的**月份**（YYYY-MM，月度精度——事件日精度已聚合）

- `event_type`：事件类型，∈ {policy, industry, overseas}，只用于分组统计

***

## 3. 五个函数，逐个说明

全部在 `framework/evaluation.py` 中实现，**签名和返回格式不许改**。

### 3.1 `rank_ic(factor, fwd_ret) -> float`

**做什么**：同一个月份截面上，因子值排名与未来收益排名的相关性（Spearman）。

**步骤**：

1. 两个 Series 按 index（code）对齐，丢掉任一缺失的样本
2. 有效样本 < 10 → 返回 `float("nan")`（不报错）
3. 返回 `scipy.stats.spearmanr(factor, fwd_ret).statistic`

**直觉**：IC = +0.05 表示"因子值越高的股票，下个月收益越高的倾向越明显"。IC 持续为正 = 因子有效。

### 3.2 `ic_series(factor_frame, ret_col="ret_fwd20") -> pd.Series`

**做什么**：对面板里每个月份各算一次 rank\_ic，得到 IC 时间序列。

- 输入长表 `[date, code, factor, ret_col]`，按 `date` 分组，每组调你的 `rank_ic`

- 返回 `pd.Series`，index=date，values=当期 IC

### 3.3 `icir(ic) -> float`

`mean(ic) / std(ic, ddof=1)`。IC 均值是"因子有多强"，ICIR 是"强得稳不稳"。

### 3.4 `bh_fdr(pvalues, q=0.05) -> pd.Series(bool)`

**做什么**：多重检验校正。同时检验 100 个因子时，裸 p<0.05 平均会冤出 5 个假阳性。BH 程序控制"假发现率"（FDR）。

**算法**（Benjamini-Hochberg）：

1. p 值升序排列：p(1) ≤ p(2) ≤ ... ≤ p(m)
2. 找最大的 k，使得 p(k) ≤ (k/m)·q
3. 前 k 个检验拒绝原假设（返回 True），其余 False

**对照**：你的输出必须与 `statsmodels.stats.multitest.multipletests(pvals, method="fdr_bh")[0]` 逐点一致。

### 3.5 `event_study(events, panel, windows=(1, 2, 3, 6)) -> pd.DataFrame`

**做什么**：事件发生后的 w 个月里，事件股票的累计超额收益（个股 − 基准）平均是多少、t 检验是否显著。

**口径（月度近似，务必照此实现）**：

- 事件发生在月份 M（events 表 date 列）

- 事件后第 1 个月收益 = 面板中该 code 在 `date=M` 行的 `ret_fwd20`

- 事件后第 2 个月收益 = `date=M+1` 行的 `ret_fwd20`，以此类推（按该 code 的 date 序列顺延，允许缺月——缺则该事件该窗口剔除并计数）

- 窗口 w 个月的累计收益 = 各月收益链式复合：Π(1+r\_i) − 1

- 超额 = 个股累计 − 基准同期累计（基准用 `bench_ret_fwd20` 同法复合）

- 每个窗口输出一行：`window, n_events, mean_excess, t_stat, p_value`（t 检验：超额均值是否为 0）

**手工算例**（用具体数字走一遍）：

```
事件: date=2016-01, code=000001.SZ, window=2
面板:
  000001.SZ 2016-01 行 ret_fwd20 = 0.0400, bench = 0.0502
  000001.SZ 2016-02 行 ret_fwd20 = 0.0962, bench = 0.1016
个股累计 = (1.0400)×(1.0962) − 1 = 0.1400
基准累计 = (1.0502)×(1.1016) − 1 = 0.1569
超额 = 0.1400 − 0.1569 = −0.0169
```

300 条事件各算一份，得到 300 个超额 → 均值、t 统计量、p 值。

**边界**：

- 事件股在面板里找不到，或后续月份不足 → 该事件该窗口剔除，**在研究报告里计数说明**

- 某窗口有效事件数 < 10 → 该行 t/p 可为 NaN，但要在报告中注明

***

## 4. 验收标准（逐条自查清单）

| # | 验收项                                    | 怎么自查                                                           |
| - | -------------------------------------- | -------------------------------------------------------------- |
| 1 | `bh_fdr` 与 statsmodels 逐点一致            | 随机生成 1000 组 p 值，两边结果完全相等                                       |
| 2 | `rank_ic` 与 `scipy.stats.spearmanr` 一致 | 同一输入对比输出                                                       |
| 3 | `event_study` 注入已知漂移可复现                | 构造假面板：把事件股的 ret\_fwd20 人为 +2%，估计出的 mean\_excess 应 ≈ +2%（±0.1%） |
| 4 | 数据不足窗口 → 剔除并计数                         | 造一个 2025-11（最末月）的事件，验证不报错且被剔除计数                                |
| 5 | 有效样本 < 10 → NaN 不报错                    | rank\_ic / event\_study 各造一例                                   |
| 6 | 输入含 NaN 自动剔除                           | 往输入里塞 NaN                                                      |
| 7 | pytest 全绿                              | `pytest tests/ -v`                                             |
| 8 | 研究报告 `reports/TASK-001-report.md`      | 见下                                                             |

**研究报告要求**：

1. 用 `panel_monthly.csv.gz` + `events_sample.csv` 完整跑一遍
2. 事件研究结果表（4 个窗口 × 全体事件，可选按 event\_type 分组）
3. 一段结论：超额是否显著？哪个窗口最强？
4. 附一组对比：同一批 p 值上，BH-FDR 与 Bonferroni 各拒绝几个

***

## 5. 常见困惑 FAQ

**Q1：面板里没有 factor 列，rank\_ic 的 factor 从哪来？**
因子要你自己从已有列构造。示例：`examples/quickstart.py` 用 close 造了 1 个月动量。本任务中 `ic_series` 的 `factor_frame` 入参就是"你已经把 factor 列拼进去"的长表。

**Q2：事件是月度精度，会不会太粗？**
会，这是本数据包的口径限制（事件日已聚合到月）。本任务验证的是方法论与代码正确性；生产环境另有日频口径，方法完全相同。

**Q3：events 里有面板不存在的 code 怎么办？**
剔除并在报告中计数（预期会有少量）。

**Q4：能不能加依赖？**
默认只能用 requirements.txt 里的 5 个。确需新增，在 PR 描述里说明理由。

**Q5：可以改 evaluation.py 的函数签名吗？**
不可以。docstring 即契约。

***

## 6. 流程

1. 交一页纸预注册方案（你假设事件超额是什么方向/量级？什么结果算证伪？）
2. 方案拍板后实现 + 测试
3. PR 提交：代码 + 测试 + 研究报告

## 禁止事项

- 不得修改接口签名

- 不得引入 requirements.txt 之外的依赖（确需新增先在 PR 里说明理由）

- 不得在代码中硬编码任何绝对路径

- 数据文件不入库、不外传

