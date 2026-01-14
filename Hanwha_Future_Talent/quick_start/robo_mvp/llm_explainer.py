# robo_mvp/llm_explainer.py
from __future__ import annotations

import json
from dataclasses import is_dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

# mvp용 키
GEMINI_API_KEY = "AIzaSyCeCAm63QB8s6aOs4xAO7A61vU1fSuSUM4"

from google import genai


# -----------------------------
# 1) 사람이 읽는 이름 사전(번역용)
# -----------------------------
FEATURE_LABELS = {
    "px_eom": "월말 종가",
    "ret_1m": "최근 1개월 수익률",
    "ret_3m": "최근 3개월 수익률",
    "ret_12m": "최근 12개월 수익률",
    "vol_3m": "최근 3개월 변동성(월수익률 표준편차)",
    "dd_6m": "최근 6개월 최대낙폭",
    "dd_12m": "최근 12개월 최대낙폭",
}

REGIME_LABELS = {
    "RISK_ON": "위험선호 장세(공격 모드)",
    "RISK_ON_VOL": "위험선호지만 변동성 큼(공격+주의)",
    "DEFENSIVE": "방어적 장세(안정 선호)",
    "RISK_OFF": "위험회피 장세(방어 모드)",
}

PROFILE_LABELS = {
    "CONSERVATIVE": "안정형",
    "AGGRESSIVE": "위험감수형",
}

DIRECTION_LABELS = {
    "up": "비중을 늘리는 방향(↑)에 기여",
    "down": "비중을 줄이는 방향(↓)에 기여",
}


# -----------------------------
# 2) JSON 직렬화 안전 변환
# -----------------------------
def _json_safe(obj: Any) -> Any:
    if is_dataclass(obj):
        return _json_safe(asdict(obj))

    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]

    # pandas
    try:
        import pandas as pd  # type: ignore
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
        if isinstance(obj, pd.Series):
            return obj.to_dict()
    except Exception:
        pass

    # numpy
    try:
        import numpy as np  # type: ignore
        if hasattr(np, "isfinite") and isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        if hasattr(np, "isfinite") and isinstance(obj, (np.floating, np.float64)):
            if not np.isfinite(obj):
                return None
            return float(obj)
        if isinstance(obj, np.ndarray):
            return _json_safe(obj.tolist())
    except Exception:
        pass

    # datetime/date
    try:
        import datetime
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
    except Exception:
        pass

    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    return str(obj)


def _pct(x: Optional[float]) -> Optional[float]:
    """0.1234 -> 12.34(%) 형태로 보기 좋게 변환용. None이면 None."""
    if x is None:
        return None
    try:
        return round(float(x) * 100.0, 2)
    except Exception:
        return None


def _to_asset_name_map(asset_master: Any) -> Dict[str, str]:
    """
    asset_master_df가 들어오면 asset_id -> (asset_name 또는 ticker 기반 사람용 이름) 매핑 생성
    기대 컬럼: asset_id, asset_name, ticker (etl.py의 asset_master_df 구조)
    """
    m: Dict[str, str] = {}
    try:
        import pandas as pd  # type: ignore
        if isinstance(asset_master, pd.DataFrame) and "asset_id" in asset_master.columns:
            for _, r in asset_master.iterrows():
                aid = str(r.get("asset_id"))
                an = r.get("asset_name")
                tk = r.get("ticker")
                # asset_name이 있으면 우선 사용, 없으면 ticker/asset_id로 대체
                label = str(an) if an and str(an) != "nan" else (str(tk) if tk else aid)
                m[aid] = label
    except Exception:
        pass
    return m


# -----------------------------
# 3) report를 LLM용으로 "번역/정리"한 payload 만들기
# -----------------------------
def build_explain_payload(report: Dict[str, Any], asset_name_map: Dict[str, str]) -> Dict[str, Any]:
    """
    report_user/report_opp에서 설명에 필요한 것만 뽑아
    - 자산명/변수명/국면명 모두 풀어쓴 형태로 정리
    """
    report = _json_safe(report)

    meta = report.get("meta", {})
    portfolio = report.get("portfolio", report.get("portfolio_user", report.get("portfolio_user_weights")))
    xai = report.get("xai", report.get("xai_user", report.get("xai_user_top")))

    # 1) 메타(국면/정책/시점/성향)
    eom = meta.get("eom") or meta.get("demo_eom")
    regime = meta.get("regime") or meta.get("regime_code")
    policy = meta.get("policy") or meta.get("policy_name")
    profile = meta.get("profile") or meta.get("user_profile")

    meta_out = {
        "기준월말(eom)": eom,
        "시장국면": REGIME_LABELS.get(str(regime), str(regime)),
        "적용정책": policy,
        "투자성향": PROFILE_LABELS.get(str(profile), str(profile)),
    }

    # 2) 포트폴리오 비중(자산명 풀어서 %로)
    weights_out: List[Dict[str, Any]] = []
    if isinstance(portfolio, list):
        # list of dict 형태 (asset_id, weight)
        for r in portfolio:
            aid = str(r.get("asset_id") or r.get("asset") or r.get("id"))
            w = r.get("weight")
            weights_out.append({
                "자산": asset_name_map.get(aid, aid),
                "비중(%)": _pct(w),
            })
    elif isinstance(portfolio, dict):
        # dict 형태 (asset_id -> weight)
        for aid, w in portfolio.items():
            weights_out.append({
                "자산": asset_name_map.get(str(aid), str(aid)),
                "비중(%)": _pct(w),
            })

    # 3) XAI 상위 요인(변수명 풀어서)
    xai_out: List[Dict[str, Any]] = []
    if isinstance(xai, list):
        for r in xai:
            # 예: {"feature":"KR_EQ_EWY.ret_1m", "value":..., "shap":..., "direction":"up"}
            feat = str(r.get("feature") or r.get("name") or "")
            direction = str(r.get("direction") or "")
            impact = r.get("impact") if "impact" in r else r.get("shap")

            # feature가 "ASSET.FEATURE" 형태면 분해
            asset_part = None
            feature_part = feat
            if "." in feat:
                asset_part, feature_part = feat.split(".", 1)

            pretty_feat = FEATURE_LABELS.get(feature_part, feature_part)
            if asset_part:
                pretty_feat = f"{asset_name_map.get(asset_part, asset_part)} / {pretty_feat}"

            xai_out.append({
                "요인": pretty_feat,
                "영향(절대값)": None if impact is None else round(float(impact), 4),
                "방향": DIRECTION_LABELS.get(direction, direction),
            })

    return {
        "meta": meta_out,
        "portfolio": weights_out,
        "xai_top_factors": xai_out,
    }


# -----------------------------
# 4) 프롬프트
# -----------------------------
def build_prompt(payload_user: Dict[str, Any], payload_opp: Dict[str, Any]) -> str:
    return f"""
너는 로보어드바이저 MVP의 설명자야. 아래 두 결과를 비교해서 사용자가 이해하기 쉽게 설명해.

[출력 형식]
1) 한 문장 요약
2) 이번 달 시장국면 설명 (2~3문장)
3) 사용자 성향 포트폴리오 추천
   - 자산 비중(%) bullet
   - 왜 이렇게 배분했는지: 핵심 이유 3개 (국면 + XAI 요인 연결)
4) 반대 성향 포트폴리오(비교)
   - 자산 비중(%) bullet
   - 무엇이 달라졌는지 2~3문장
5) 주의/다음 액션 (월 1회 리밸런싱 기준, 2~3문장)

[XAI 해석 규칙(매우 중요)]
- xai_top_factors의 "방향"은 시장이 오를/내릴 신호가 아니다.
- "방향"은 '해당 요인이 포트폴리오 추천 결과(비중)에 어떤 방향으로 작용했는지'를 뜻한다.
  - "비중을 늘리는 방향(↑)에 기여" = 그 요인이 특정 자산(또는 위험자산/주식총비중)의 비중을 높이도록 밀어줌
  - "비중을 줄이는 방향(↓)에 기여" = 그 요인이 특정 자산(또는 위험자산/주식총비중)의 비중을 낮추도록 밀어줌
- 따라서 "UP 요인이 존재하지만 DOWN 요인이 크다 → 시장 하락 압력" 같은 표현을 쓰지 말 것.
- XAI는 "원인 → 비중 변화" 형태로만 설명할 것.
  예: "최근 6개월 최대낙폭이 커서(요인), 주식 비중을 줄이고(결과), 채권/현금 비중을 늘렸다(대체 결과)."
- "영향(절대값)"은 중요도(기여 크기)로 해석하되, 인과/확률/확신 표현은 금지.
- 요인이 '어느 자산의 어떤 지표'인지 반드시 붙여서 말할 것:
  예: "미국 주식(VTI) / 최근 3개월 변동성" 같은 방식


[사용자 결과]
{json.dumps(payload_user, ensure_ascii=False, indent=2)}

[반대 성향 결과]
{json.dumps(payload_opp, ensure_ascii=False, indent=2)}
""".strip()


# -----------------------------
# 5) Gemini 호출
# -----------------------------
def explain_reports_with_gemini(report_user: Dict[str, Any],
                                report_opp: Dict[str, Any],
                                asset_master_df: Any,
                                model: str = "gemini-2.5-flash",
                                temperature: float = 0.4) -> str:
    if not GEMINI_API_KEY or GEMINI_API_KEY == "PUT_YOUR_GEMINI_API_KEY_HERE":
        raise RuntimeError("llm_explainer.py의 GEMINI_API_KEY에 실제 키를 넣어줘.")

    client = genai.Client(api_key=GEMINI_API_KEY)

    asset_name_map = _to_asset_name_map(asset_master_df)

    payload_user = build_explain_payload(report_user, asset_name_map)
    payload_opp = build_explain_payload(report_opp, asset_name_map)

    prompt = build_prompt(payload_user, payload_opp)

    resp = client.models.generate_content(
        model=model,
        contents=prompt,
        # temperature를 옵션으로 넣고 싶으면 SDK 버전에 따라 위치가 달라질 수 있음
        # MVP에서는 기본값으로도 충분히 자연스럽게 나옴
    )
    return resp.text or ""
