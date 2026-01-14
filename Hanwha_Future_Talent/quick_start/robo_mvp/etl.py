from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
import requests
import numpy as np
import pandas as pd
import os
import tempfile
from pathlib import Path
from datetime import datetime


@dataclass(frozen=True)
class AssetSpec:
    asset_id: str
    asset_name: str
    asset_class: str
    ticker: str
    currency: str = "USD"
    is_active: int = 1

def _default_cache_dir() -> Path:
    # OS 임시폴더 아래 robo_mvp_cache 생성 (경로를 사용자가 신경쓸 필요 없음)
    d = Path(tempfile.gettempdir()) / "robo_mvp_cache"
    d.mkdir(parents=True, exist_ok=True)
    return d

def fetch_stooq_daily(
    ticker: str,
    timeout: int = 120,
    prefer_cache: bool = True,
    cache_dir: str | None = None,
    force_refresh: bool = False
) -> pd.DataFrame:
    """
    Stooq CSV를 받아서 일별 OHLCV DataFrame으로 반환.
    반환 컬럼(표준):
      date, open, high, low, close, volume
    """
    cache_base = Path(cache_dir) if cache_dir else _default_cache_dir()
    fname = f"{ticker.upper().replace('.', '_')}_daily.csv"
    fpath = cache_base / fname

    # 1) 캐시 or 온라인 CSV 읽기
    if prefer_cache and (not force_refresh) and fpath.exists():
        df = pd.read_csv(fpath)
    else:
        url = "https://stooq.com/q/d/l/"
        params = {"s": ticker, "i": "d"}
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text))
        df.to_csv(fpath, index=False)

    if df.empty:
        raise ValueError(f"No data returned for ticker={ticker}")

    # 2) 여기서 “단 한 번” 표준 컬럼명으로 통일
    df = df.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    })

    # 일부 CSV가 이미 소문자일 수도 있으니 안전 처리
    df.columns = [c.lower() for c in df.columns]

    # 3) 타입 정리
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for c in ["open", "high", "low", "close", "volume"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.sort_values("date").reset_index(drop=True)

    # 4) 최종 표준 스키마 보장
    return df[["date", "open", "high", "low", "close", "volume"]]


def make_monthly_features(daily: pd.DataFrame) -> pd.DataFrame:
    """
    일별 OHLCV -> 월말 기준 feature 생성
    - px_eom: 월말 종가
    - ret_1m/3m/12m: 월말 종가 기반 단순 수익률(pct_change)
    - vol_3m: 월별 수익률(ret_1m)의 최근 3개월 표준편차
    - dd_6m/dd_12m: 월말 종가 기준 최근 6/12개월 최대낙폭
    """
    df = daily.copy()
    df["eom"] = df["date"].dt.to_period("M").dt.to_timestamp("M")

    # 월말 종가
    px = df.groupby("eom", as_index=False)["close"].last().rename(columns={"close": "px_eom"})

    # 월 수익률(단순)
    px["ret_1m"] = px["px_eom"].pct_change(1)
    px["ret_3m"] = px["px_eom"].pct_change(3)
    px["ret_12m"] = px["px_eom"].pct_change(12)

    # 3개월 변동성(월 수익률 기준)
    px["vol_3m"] = px["ret_1m"].rolling(3).std(ddof=0)

    # 최대낙폭(dd): 기간 내 최고점 대비 현재의 하락률 최저치
    def rolling_dd(series: pd.Series, window: int) -> pd.Series:
        out = []
        vals = series.to_numpy(dtype=float)
        for i in range(len(vals)):
            j0 = max(0, i - window + 1)
            window_vals = vals[j0:i+1]
            if len(window_vals) == 0 or np.isnan(window_vals).all():
                out.append(np.nan)
                continue
            peak = np.nanmax(window_vals)
            if peak <= 0 or np.isnan(peak):
                out.append(np.nan)
                continue
            dd = (vals[i] / peak) - 1.0
            out.append(dd)
        return pd.Series(out, index=series.index)

    px["dd_6m"] = rolling_dd(px["px_eom"], 6)
    px["dd_12m"] = rolling_dd(px["px_eom"], 12)

    return px[["eom", "px_eom", "ret_1m", "ret_3m", "ret_12m", "vol_3m", "dd_6m", "dd_12m"]]

def run_etl(assets: list[AssetSpec]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    (1) asset_master 생성
    (2) raw_price_daily 생성 (모든 자산 합친 long format)
    (3) feat_asset_monthly 생성 (모든 자산 합친 long format)
    반환:
      asset_master_df, raw_price_daily_df, feat_asset_monthly_df
    """
    asset_master_df = pd.DataFrame([a.__dict__ for a in assets])

    daily_rows = []
    monthly_rows = []

    for a in assets:
        daily = fetch_stooq_daily(a.ticker)
        daily["asset_id"] = a.asset_id
        daily_rows.append(daily)

        feat = make_monthly_features(daily)
        feat["asset_id"] = a.asset_id
        monthly_rows.append(feat)

    raw_price_daily_df = pd.concat(daily_rows, ignore_index=True)
    feat_asset_monthly_df = pd.concat(monthly_rows, ignore_index=True)

    # 키 중복 정리(CSV/DB 없이도 안정성 확보)
    raw_price_daily_df = raw_price_daily_df.drop_duplicates(["asset_id", "date"]).sort_values(["asset_id", "date"])
    feat_asset_monthly_df = feat_asset_monthly_df.drop_duplicates(["asset_id", "eom"]).sort_values(["asset_id", "eom"])

    return asset_master_df, raw_price_daily_df, feat_asset_monthly_df