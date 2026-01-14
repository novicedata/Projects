from __future__ import annotations

import numpy as np
import pandas as pd

REGIMES = ["RISK_ON", "RISK_ON_VOL", "DEFENSIVE", "RISK_OFF"]

def _pivot_feat(feat_asset_monthly: pd.DataFrame, equity_assets: list[str]) -> pd.DataFrame:
    """
    월별 상태를 만들기 위한 보조: equity(주식) 대표 지표를 만들기 위해 wide로 변환
    """
    f = feat_asset_monthly.copy()
    f["eom"] = pd.to_datetime(f["eom"])
    # 주식 자산만 골라 평균(단순 MVP)
    eq = f[f["asset_id"].isin(equity_assets)].copy()

    # 월별 주식 ret_1m 평균, vol_3m 평균, dd_6m 평균
    g = eq.groupby("eom", as_index=False).agg(
        eq_ret_1m=("ret_1m", "mean"),
        eq_vol_3m=("vol_3m", "mean"),
        eq_dd_6m=("dd_6m", "mean"),
    )
    return g.sort_values("eom").reset_index(drop=True)


def classify_regime_simple(feat_asset_monthly: pd.DataFrame, equity_assets: list[str]) -> pd.DataFrame:
    """
    4국면 간단 규칙 기반 분류(MVP):
    - 주식 평균 월수익률(eq_ret_1m)과 변동성(eq_vol_3m), 낙폭(eq_dd_6m)을 사용
    - 기준값은 데이터 분위수로 자동 보정 (하드코딩 최소화)
    """
    s = _pivot_feat(feat_asset_monthly, equity_assets)

    # 분위수 기반 컷(데이터 적응형)
    ret_hi = np.nanquantile(s["eq_ret_1m"], 0.60)
    ret_lo = np.nanquantile(s["eq_ret_1m"], 0.40)
    vol_hi = np.nanquantile(s["eq_vol_3m"], 0.65)
    dd_bad = np.nanquantile(s["eq_dd_6m"], 0.35)  # dd는 음수(더 낮을수록 나쁨)

    def decide(row):
        r = row["eq_ret_1m"]
        v = row["eq_vol_3m"]
        d = row["eq_dd_6m"]

        # 방어/리스크오프: 수익률이 낮거나 dd가 나쁠 때
        if (not np.isnan(d) and d <= dd_bad) and (np.isnan(r) or r <= ret_lo):
            return "RISK_OFF"
        if (np.isnan(r) or r <= ret_lo):
            return "DEFENSIVE"

        # 리스크온: 수익률이 높음
        if (not np.isnan(v) and v >= vol_hi):
            return "RISK_ON_VOL"
        return "RISK_ON"

    s["regime_code"] = s.apply(decide, axis=1)

    out = s[["eom", "regime_code", "eq_ret_1m", "eq_vol_3m", "eq_dd_6m"]].copy()
    return out
