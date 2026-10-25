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
    windows: tuple[int, ...] = (1, 2, 5, 10),
) -> pd.DataFrame:
    """事件研究：事件日后 N 日累计超额收益。

    Parameters
    ----------
    events : pd.DataFrame
        列 [date, code]（可含 event_type 仅作分组统计用）。
    panel : pd.DataFrame
        长表，列至少含 [date, code, ret_fwd1(次日收益), bench_ret_fwd1]，
        交易日频率，按 (code, date) 排序。
    windows : tuple[int, ...]
        观察窗口（交易日）。

    Returns
    -------
    pd.DataFrame
        每行一个 (window,)：列 [window, n_events, mean_excess, t_stat, p_value]，
        超额=个股累计收益-基准同期累计收益。
    """
    raise NotImplementedError
