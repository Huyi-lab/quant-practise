"""评估框架：统一接口契约。

所有任务包产出的评估代码必须实现本模块定义的函数签名，
输入输出格式以本模块 docstring 为唯一标准。
"""
from __future__ import annotations

import pandas as pd


def rank_ic(factor: pd.Series, fwd_ret: pd.Series) -> float:
    """单期 Spearman 秩相关。

    Parameters
    ----------
    factor : pd.Series
        截面因子值，index=code。
    fwd_ret : pd.Series
        同期未来收益，index=code，与 factor 对齐。

    Returns
    -------
    float
        Spearman 秩相关系数；有效样本 < 10 返回 float("nan")。
    """
    raise NotImplementedError


def ic_series(factor_frame: pd.DataFrame, ret_col: str = "ret_fwd20") -> pd.Series:
    """逐期 RankIC 序列。

    Parameters
    ----------
    factor_frame : pd.DataFrame
        长表，列至少含 [date, code, factor, ret_col]。
    ret_col : str
        未来收益列名。

    Returns
    -------
    pd.Series
        index=date，values=当期 RankIC。
    """
    raise NotImplementedError


def icir(ic: pd.Series) -> float:
    """ICIR = mean(ic) / std(ic, ddof=1)。"""
    raise NotImplementedError


def bh_fdr(pvalues: pd.Series, q: float = 0.05) -> pd.Series:
    """Benjamini-Hochberg FDR 控制。

    Parameters
    ----------
    pvalues : pd.Series
        各检验的 p 值（保留原 index）。
    q : float
        FDR 控制水平。

    Returns
    -------
    pd.Series（bool）
        True=拒绝原假设。要求与 statsmodels multipletests(method="fdr_bh") 逐点一致。
    """
    raise NotImplementedError


def event_study(
    events: pd.DataFrame,
    panel: pd.DataFrame,
    windows: tuple[int, ...] = (1, 2, 3, 6),
) -> pd.DataFrame:
    """事件研究（月度口径）：事件月后 w 个月累计超额收益。

    Parameters
    ----------
    events : pd.DataFrame
        列 [date, code]（可含 event_type 仅作分组统计用）。
        date 格式 YYYY-MM（事件发生的月份，月度精度）。
    panel : pd.DataFrame
        长表，列至少含 [date, code, ret_fwd20, bench_ret_fwd20]，
        月度频率（date=YYYY-MM 月末标签），按 (code, date) 排序。
        面板中 date=M 行的 ret_fwd20 = M 月末之后约 1 个月（20 交易日）的收益，
        即"事件后第 1 个月收益"。
    windows : tuple[int, ...]
        观察窗口，单位=月。窗口 w 的累计收益 = 事件月起 w 个月收益链式复合
        Π(1+r_i) − 1；超额 = 个股累计 − 基准同期累计。

    Returns
    -------
    pd.DataFrame
        每行一个 window：列 [window, n_events, mean_excess, t_stat, p_value]。
        事件股在面板缺失或后续月份不足的，该事件该窗口剔除（实现中需计数，
        供报告披露）；某窗口有效事件数 < 10 时该行 t_stat/p_value 可为 NaN。
    """
    raise NotImplementedError
