"""Quickstart 示例：从数据包到 IC 评估的最小闭环

本示例演示：
  1. 如何读取离线分发的月度面板数据（data/panel_monthly.csv.gz）
  2. 如何从价格列构造一个可复现的截面因子（1个月动量）
  3. 如何用 Spearman 秩相关计算逐期 RankIC，并汇总 IC 均值 / ICIR

说明：
- 本示例自包含，不依赖 framework/（framework 的正式实现是 TASK-001 的任务内容；
  完成后你可以把本文件的手工计算替换为 framework.evaluation.ic_series / icir 对照验证）
- 只使用 requirements.txt 内依赖；数据文件需自行放入 data/（不入库）

运行：python examples/quickstart.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

DATA = Path(__file__).resolve().parent.parent / "data" / "panel_monthly.csv.gz"

MIN_CROSS_SECTION = 10  # 截面有效样本下限，与 framework 口径一致


def load_panel(path: Path = DATA) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"未找到 {path}；数据包由项目方离线分发，请放入 data/ 后重试")
    df = pd.read_csv(path)
    need = {"date", "code", "close", "ret_fwd20"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"面板缺少列: {missing}")
    return df


def build_factor_mom1(panel: pd.DataFrame) -> pd.Series:
    """1个月动量因子 = 当月收盘 / 上月收盘 - 1（按 code 分组差分）。

    仅作演示：真实任务中因子定义以工单接口契约为准。
    """
    p = panel.sort_values(["code", "date"])
    prev = p.groupby("code")["close"].shift(1)
    mom = p["close"] / prev - 1.0
    return mom.where(prev > 0)


def monthly_rank_ic(df: pd.DataFrame, factor_col: str,
                    label_col: str = "ret_fwd20") -> pd.Series:
    """逐月截面 Spearman 秩相关（RankIC）。样本不足返回 NaN。"""
    ics = {}
    for dt, g in df.groupby("date"):
        pair = g[[factor_col, label_col]].dropna()
        if len(pair) < MIN_CROSS_SECTION:
            ics[dt] = np.nan
            continue
        ic, _ = spearmanr(pair[factor_col], pair[label_col])
        ics[dt] = ic
    return pd.Series(ics, name="rank_ic")


def main() -> None:
    panel = load_panel()
    panel["mom1"] = build_factor_mom1(panel)

    ic = monthly_rank_ic(panel, "mom1")
    valid = ic.dropna()

    print(f"面板: {panel['date'].nunique()} 个月度截面, "
          f"{panel['code'].nunique()} 只标的, 共 {len(panel)} 行")
    print(f"有效IC期数: {len(valid)} / {len(ic)}")
    print(f"IC 均值 : {valid.mean():+.4f}")
    print(f"ICIR    : {valid.mean() / valid.std(ddof=1):+.4f}")
    print(f"IC>0 占比: {(valid > 0).mean() * 100:.1f}%")
    print("\n最近5期 RankIC:")
    print(valid.tail(5).round(4).to_string())


if __name__ == "__main__":
    main()
