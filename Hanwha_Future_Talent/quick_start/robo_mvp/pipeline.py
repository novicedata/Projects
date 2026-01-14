import json
import numpy as np
import pandas as pd
from dataclasses import dataclass
from scipy.optimize import minimize


# =====================================================
# A) 공용 변수 설정
# =====================================================

PROFILES = ["CONSERVATIVE", "AGGRESSIVE"]
REGIMES = ["RISK_ON", "RISK_ON_VOL", "DEFENSIVE", "RISK_OFF"]

ASSET_FEATURES = ["ret_1m", "ret_3m", "ret_12m", "vol_3m", "dd_6m", "dd_12m"]


# -------------------------
# 공통 유틸
# -------------------------
def one_hot(value: str, categories: list[str]) -> np.ndarray:
    return np.array([1.0 if value == c else 0.0 for c in categories], dtype=float)

def safe_float(x, default=np.nan):
    try:
        if x is None:
            return default
        if isinstance(x, str) and x.strip() == "":
            return default
        v = float(x)
        return v
    except Exception:
        return default

def zfill_nan_to_zero(x: np.ndarray) -> np.ndarray:
    x = np.array(x, dtype=float)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    return x


# =====================================================
# B) 데이터 로더 (DF 기반 Quick Start)
#    - etl.py 결과(feat_asset_monthly) + regime.py 결과(regime_monthly)를 그대로 받는다
# =====================================================

def infer_equity_assets(assets: list[str], asset_master: pd.DataFrame) -> list[str]:
    """A방안: asset_master.asset_class에 'EQ' 포함이면 주식자산으로 간주."""
    am = asset_master[asset_master["asset_id"].isin(assets)].copy()
    eq = am[am["asset_class"].astype(str).str.contains("EQ", na=False)]["asset_id"].tolist()
    return [a for a in assets if a in eq]

def load_state(regime_monthly: pd.DataFrame,
               feat_asset_monthly: pd.DataFrame,
               eom: pd.Timestamp,
               assets: list[str]) -> dict:
    """노트북 load_state(engine, eom)와 동일 의미. 단, DB 대신 DF에서 필터링."""
    eom = pd.to_datetime(eom)
    reg = regime_monthly[regime_monthly["eom"] == eom]
    if reg.empty:
        raise RuntimeError(f"regime_monthly missing: {eom.date()}")
    regime = reg.iloc[0]["regime_code"] if "regime_code" in reg.columns else reg.iloc[0]["regime"]

    feat = feat_asset_monthly[(feat_asset_monthly["eom"] == eom) & (feat_asset_monthly["asset_id"].isin(assets))].copy()
    missing = set(assets) - set(feat["asset_id"].tolist())
    if missing:
        raise RuntimeError(f"feat_asset_monthly missing assets @ {eom.date()}: {sorted(missing)}")

    feat = feat.set_index("asset_id").reindex(assets).reset_index()
    return {"eom": eom, "regime": regime, "feat": feat}

def load_ret_wide(feat_asset_monthly: pd.DataFrame, assets: list[str]) -> pd.DataFrame:
    df = feat_asset_monthly.copy()
    df["eom"] = pd.to_datetime(df["eom"])

    # 데이터에 실제 존재하는 asset_id만 남김
    available = set(df["asset_id"].unique())
    missing = [a for a in assets if a not in available]
    if missing:
        raise RuntimeError(f"assets not found in feat_asset_monthly.asset_id: {missing}")

    df = df[df["asset_id"].isin(assets) & df["ret_1m"].notna()]

    wide = df.pivot(index="eom", columns="asset_id", values="ret_1m")

    # 컬럼 순서만 맞추되, 존재하지 않는 컬럼을 억지로 만들지 않음
    wide = wide[assets]
    wide = wide.sort_index()

    return wide


def get_common_eoms(regime_monthly: pd.DataFrame,
                    feat_asset_monthly: pd.DataFrame,
                    assets: list[str],
                    min_assets: int | None = None) -> list[pd.Timestamp]:
    """노트북 get_common_eoms(engine, min_assets=5)와 동일 의미(DF 버전)."""
    if min_assets is None:
        min_assets = len(assets)

    reg_eoms = pd.to_datetime(regime_monthly["eom"]).drop_duplicates().sort_values()
    feat_ok = (
        feat_asset_monthly[feat_asset_monthly["asset_id"].isin(assets)]
        .groupby("eom")["asset_id"].nunique()
        .reset_index(name="n_assets")
    )
    feat_ok = feat_ok[feat_ok["n_assets"] >= int(min_assets)]
    feat_ok_eoms = pd.to_datetime(feat_ok["eom"]).drop_duplicates()

    common = pd.Index(reg_eoms).intersection(pd.Index(feat_ok_eoms))
    return pd.to_datetime(common).sort_values().to_list()


# =====================================================
# C) 공분산/상관
# =====================================================

def estimate_global_corr(ret_wide: pd.DataFrame, window_months: int = 60) -> np.ndarray:
    hist = ret_wide.tail(window_months).dropna(how="any")
    if len(hist) < 12:
        n = ret_wide.shape[1]
        C = np.eye(n)
        C[C == 0] = 0.10
        return C
    C = np.corrcoef(hist.values.T)
    C = np.nan_to_num(C, nan=0.0, posinf=0.0, neginf=0.0)
    np.fill_diagonal(C, 1.0)
    return C

def approx_cov_from_X(x: np.ndarray, corr: np.ndarray) -> np.ndarray:
    """노트북 approx_cov_from_X(x, corr): X에서 vol_3m을 꺼내 Sigma를 근사."""
    offset = len(REGIMES) + len(PROFILES)
    block = len(ASSET_FEATURES)
    f_idx = {f: i for i, f in enumerate(ASSET_FEATURES)}
    vol_col = f_idx["vol_3m"]

    vols = []
    n_assets = (len(x) - offset) // block
    for j in range(n_assets):
        base = offset + j * block
        vols.append(max(0.0, safe_float(x[base + vol_col], 0.0)))
    vols = np.array(vols, dtype=float)
    vols = np.where(vols <= 1e-12, 1e-6, vols)

    D = np.diag(vols)
    Sigma = D @ corr @ D
    Sigma = np.nan_to_num(Sigma, nan=0.0, posinf=0.0, neginf=0.0)
    return Sigma


# =====================================================
# D) μ 예측 모델 (PRED_MVO)
# =====================================================

@dataclass
class MuModel:
    """
    단순화를 위해 sklearn 기반 모델을 사용.
    - 입력: (asset_id one-hot 없이) X에서 자산별 피처를 뽑아 구성
    - 출력: 다음달 기대수익(μ)
    """
    model: object
    asset_to_idx: dict

    def _mu_row(self, x_full: np.ndarray, asset_j: int, n_assets: int) -> np.ndarray:
        """
        노트북 주석 그대로:
        [regime_oh(4) + 자산별 ret/vol/dd(해당 자산 블록) + profile_oh(2)]
        """
        x_full = zfill_nan_to_zero(x_full)
        reg = x_full[:len(REGIMES)]
        prof = x_full[len(REGIMES):len(REGIMES)+len(PROFILES)]
        offset = len(REGIMES) + len(PROFILES)
        block = len(ASSET_FEATURES)
        base = offset + asset_j * block
        asset_block = x_full[base:base+block]
        return np.concatenate([reg, asset_block, prof], axis=0)

    def predict_mu(self, x: np.ndarray) -> np.ndarray:
        """x(1개 샘플) -> 자산별 μ(n_assets)"""
        n_assets = len(self.asset_to_idx)
        rows = []
        for j in range(n_assets):
            rows.append(self._mu_row(x, j, n_assets))
        X = np.vstack(rows)
        mu = self.model.predict(X).reshape(-1)
        return np.array(mu, dtype=float)


def train_mu_model(regime_monthly, feat_asset_monthly, ret_wide, assets):
    from sklearn.ensemble import HistGradientBoostingRegressor

    # 1) eom 타입 표준화 (안전)
    regime_monthly = regime_monthly.copy()
    feat_asset_monthly = feat_asset_monthly.copy()
    regime_monthly["eom"] = pd.to_datetime(regime_monthly["eom"])
    feat_asset_monthly["eom"] = pd.to_datetime(feat_asset_monthly["eom"])
    ret_wide = ret_wide.copy()
    ret_wide.index = pd.to_datetime(ret_wide.index)

    # 2) 학습에 쓸 eom은 "실제로 ret_wide에 존재하는 달" 기반으로 잡는다
    #    + assets 전부 수익률이 있는 달만 쓰면 스킵 폭발이 사라짐
    ret_full = ret_wide.dropna(how="any")  # 모든 자산 ret_1m 존재
    if len(ret_full) < 24:
        raise RuntimeError(f"Not enough full-return months: {len(ret_full)}")

    # 3) regime/feat도 있는 달과 교집합
    reg_eoms = set(regime_monthly["eom"].unique())
    # feat는 assets가 모두 있는 달만
    feat_cnt = (feat_asset_monthly[feat_asset_monthly["asset_id"].isin(assets)]
                .groupby("eom")["asset_id"].nunique())
    feat_eoms = set(feat_cnt[feat_cnt == len(assets)].index)

    usable_eoms = sorted(set(ret_full.index) & reg_eoms & feat_eoms)
    if len(usable_eoms) < 24:
        raise RuntimeError(f"Not enough usable months after intersection: {len(usable_eoms)}")

    X_train, y_train = [], []

    # 4) t_next는 달력 계산이 아니라 "다음 인덱스"로 잡는다 (핵심)
    usable_eoms = pd.to_datetime(usable_eoms)
    for i in range(len(usable_eoms) - 1):
        t = usable_eoms[i]
        t_next = usable_eoms[i + 1]

        st = load_state(regime_monthly, feat_asset_monthly, t, assets)

        for profile in PROFILES:
            x_full = state_to_X(st, profile, assets)

            for j, a in enumerate(assets):
                target = ret_wide.loc[t_next, a]
                if pd.isna(target):
                    continue

                reg = x_full[:len(REGIMES)]
                prof = x_full[len(REGIMES):len(REGIMES)+len(PROFILES)]
                offset = len(REGIMES) + len(PROFILES)
                block = len(ASSET_FEATURES)
                base = offset + j * block
                asset_block = x_full[base:base+block]
                row = np.concatenate([reg, asset_block, prof], axis=0)

                X_train.append(row)
                y_train.append(float(target))

    if len(y_train) < 200:
        raise RuntimeError(f"Not enough training rows for mu model: {len(y_train)}")

    X_train = np.vstack(X_train)
    y_train = np.array(y_train, dtype=float)

    model = HistGradientBoostingRegressor(
        max_depth=4, learning_rate=0.05, max_iter=300, random_state=42
    )
    model.fit(X_train, y_train)

    return MuModel(model=model, asset_to_idx={a: i for i, a in enumerate(assets)})



# =====================================================
# E) 공통 입력 X 구성
# =====================================================

def state_to_X(state: dict, profile: str, assets: list[str]) -> np.ndarray:
    """X = regime one-hot + profile one-hot + (자산별 feature block)"""
    regime = state["regime"]
    feat = state["feat"].copy()

    x = []
    x.extend(one_hot(regime, REGIMES))
    x.extend(one_hot(profile, PROFILES))

    feat = feat.set_index("asset_id").reindex(assets)
    for a in assets:
        row = feat.loc[a]
        for f in ASSET_FEATURES:
            x.append(safe_float(row.get(f), np.nan))
    return np.array(x, dtype=float)


# =====================================================
# F) policy 선택(국면+성향 매핑)
# =====================================================

def choose_policy(regime: str, profile: str) -> str:
    """
    정책은 많을 필요 없다고 했으니, 단순 매핑:
    - 안정형 + 나쁜국면 => MDD_GUARD
    - 위험감수형 + 좋은국면 => PRED_MVO
    - 나머지 => CAR_RP
    """
    if profile == "CONSERVATIVE" and regime in ["DEFENSIVE", "RISK_OFF"]:
        return "MDD_GUARD"
    if profile == "AGGRESSIVE" and regime in ["RISK_ON", "RISK_ON_VOL"]:
        return "PRED_MVO"
    return "CAR_RP"


# =====================================================
# G) 정책 3개 + 공통 입력을 모두 사용하되 정책별 조정
# =====================================================

@dataclass
class PolicyParams:
    corr: np.ndarray
    car_rp_equity_cap_cons: float = 0.45
    car_rp_equity_cap_aggr: float = 0.75
    mdd_equity_cap_cons: float = 0.20
    mdd_equity_cap_aggr: float = 0.35
    gamma_cons: float = 12.0
    gamma_aggr: float = 6.0
    w_max_each: float = 0.70
    mvo_equity_cap_cons: float = 0.60
    mvo_equity_cap_aggr: float = 0.90

def apply_equity_cap(w: pd.Series, equity_assets: list[str], cap: float) -> pd.Series:
    eq_sum = float(w.loc[equity_assets].sum()) if equity_assets else 0.0
    if (not equity_assets) or eq_sum <= cap:
        return w
    w = w.copy()
    w.loc[equity_assets] *= (cap / eq_sum)
    non_eq = w.index.difference(equity_assets)
    w.loc[non_eq] *= (1.0 - float(w.loc[equity_assets].sum())) / float(w.loc[non_eq].sum())
    return w

def policy_compute_weights(policy: str,
                           x: np.ndarray,
                           params: PolicyParams,
                           mu_model: MuModel | None,
                           assets: list[str],
                           equity_assets: list[str]) -> pd.Series:
    x = zfill_nan_to_zero(x)
    profile = PROFILES[int(np.argmax(x[len(REGIMES):len(REGIMES)+len(PROFILES)]))]
    regime = REGIMES[int(np.argmax(x[:len(REGIMES)]))]

    Sigma = approx_cov_from_X(x, params.corr)

    offset = len(REGIMES) + len(PROFILES)
    block = len(ASSET_FEATURES)
    f_idx = {f:i for i,f in enumerate(ASSET_FEATURES)}

    ret3, ret12, vol3, dd6, dd12 = [], [], [], [], []
    n_assets = len(assets)
    for j in range(n_assets):
        base = offset + j*block
        ret3.append(safe_float(x[base + f_idx["ret_3m"]], 0.0))
        ret12.append(safe_float(x[base + f_idx["ret_12m"]], 0.0))
        vol3.append(safe_float(x[base + f_idx["vol_3m"]], 0.0))
        dd6.append(safe_float(x[base + f_idx["dd_6m"]], 0.0))
        dd12.append(safe_float(x[base + f_idx["dd_12m"]], 0.0))

    ret3 = np.array(ret3, dtype=float)
    ret12 = np.array(ret12, dtype=float)
    vol3 = np.array(vol3, dtype=float)
    dd6 = np.array(dd6, dtype=float)
    dd12 = np.array(dd12, dtype=float)

    if policy == "CAR_RP":
        inv_vol = 1.0 / np.maximum(vol3, 1e-6)
        w = inv_vol / inv_vol.sum()
        w = pd.Series(w, index=assets)

        cap = params.car_rp_equity_cap_cons if profile == "CONSERVATIVE" else params.car_rp_equity_cap_aggr
        if regime == "RISK_OFF":
            cap *= 0.70
        elif regime == "DEFENSIVE":
            cap *= 0.85
        elif regime == "RISK_ON_VOL":
            cap *= 0.95

        w = apply_equity_cap(w, equity_assets, cap)
        w = w.clip(lower=0)
        w = w / w.sum()
        return w

    if policy == "MDD_GUARD":
        guard = (1.0 + 2.2*dd6 + 1.2*dd12) * (1.0 + 0.6*np.maximum(vol3, 0))
        momentum = 0.7*ret3 + 0.3*ret12
        guard = guard * np.exp(-0.15*momentum)

        if regime in ["DEFENSIVE", "RISK_OFF"]:
            guard *= 1.10

        score = 1.0 / np.maximum(guard, 1e-6)
        w = score / score.sum()
        w = pd.Series(w, index=assets)

        cap = params.mdd_equity_cap_cons if profile == "CONSERVATIVE" else params.mdd_equity_cap_aggr
        if regime == "RISK_OFF":
            cap *= 0.75
        elif regime == "DEFENSIVE":
            cap *= 0.85

        w = apply_equity_cap(w, equity_assets, cap)
        w = w.clip(lower=0)
        w = w / w.sum()
        return w

    if policy == "PRED_MVO":
        if mu_model is None:
            raise RuntimeError("mu_model is required for PRED_MVO")

        mu = mu_model.predict_mu(x)

        gamma = params.gamma_cons if profile == "CONSERVATIVE" else params.gamma_aggr
        w_max = params.w_max_each
        eq_cap = params.mvo_equity_cap_cons if profile == "CONSERVATIVE" else params.mvo_equity_cap_aggr

        n = len(assets)
        eq_idx = [assets.index(a) for a in equity_assets] if equity_assets else []

        w_min = np.zeros(n)
        w_max_vec = np.ones(n) * float(w_max)

        def obj(w):
            w = np.array(w, dtype=float)
            return -(w @ mu - gamma * (w @ Sigma @ w))

        cons = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
        if eq_idx:
            cons.append({"type": "ineq", "fun": lambda w, cap=eq_cap, idx=eq_idx: cap - np.sum(w[idx])})

        bounds = [(float(w_min[i]), float(w_max_vec[i])) for i in range(n)]
        x0 = np.ones(n) / n

        res = minimize(obj, x0=x0, bounds=bounds, constraints=cons, method="SLSQP")
        if not res.success:
            return policy_compute_weights("CAR_RP", x, params, mu_model, assets, equity_assets)

        w = np.clip(np.array(res.x, dtype=float), 0, 1)
        w = w / w.sum()
        return pd.Series(w, index=assets)

    raise ValueError(f"Unknown policy: {policy}")


# =====================================================
# H) Kernel SHAP
# =====================================================

def policy_target_value(policy: str,
                        x: np.ndarray,
                        params: PolicyParams,
                        mu_model: MuModel,
                        assets: list[str],
                        equity_assets: list[str],
                        target: str = "equity_total") -> float:
    w = policy_compute_weights(policy, x, params, mu_model, assets, equity_assets)
    if target == "equity_total":
        return float(w.loc[equity_assets].sum()) if equity_assets else 0.0
    if target in assets:
        return float(w.loc[target])
    raise ValueError("target must be equity_total or one of assets")

def kernel_shap_explain(policy: str,
                        x_explain: np.ndarray,
                        X_background: np.ndarray,
                        params: PolicyParams,
                        mu_model: MuModel,
                        assets: list[str],
                        equity_assets: list[str],
                        target: str = "equity_total",
                        nsamples: int = 200,
                        top_k: int = 8):
    import shap

    def f(X):
        out = []
        for i in range(X.shape[0]):
            out.append(policy_target_value(policy, X[i], params, mu_model, assets, equity_assets, target=target))
        return np.array(out, dtype=float)

    explainer = shap.KernelExplainer(f, X_background)
    sv = explainer.shap_values(x_explain.reshape(1, -1), nsamples=nsamples)
    sv = np.array(sv).reshape(-1)

    fn = []
    fn += [f"regime__{r}" for r in REGIMES]
    fn += [f"profile__{p}" for p in PROFILES]
    for a in assets:
        for feat in ASSET_FEATURES:
            fn.append(f"{a}__{feat}")

    fx = x_explain.reshape(-1)
    order = np.argsort(np.abs(sv))[::-1]
    top = []
    for j in order[:top_k]:
        top.append({
            "feature": fn[j],
            "value": float(fx[j]),
            "shap": float(sv[j]),
            "direction": "UP" if sv[j] > 0 else "DOWN"
        })

    base = explainer.expected_value
    if isinstance(base, (list, np.ndarray)):
        base_value = float(np.array(base).reshape(-1)[0])
    else:
        base_value = float(base)

    return top, base_value


# =====================================================
# I) 월 1개(eom) 기준 "최종 사용자 리포트"
# =====================================================

def opposite_profile(profile: str) -> str:
    return "AGGRESSIVE" if profile == "CONSERVATIVE" else "CONSERVATIVE"

def portfolio_to_table(weights: pd.Series,
                       eps: float = 1e-6,
                       round_decimals: int = 4) -> pd.DataFrame:
    w = weights.copy()
    w[np.abs(w) < eps] = 0.0
    w = w / w.sum() if w.sum() > 0 else w

    df = pd.DataFrame({"asset_id": w.index, "weight": w.values})
    df["weight"] = df["weight"].astype(float).round(round_decimals)
    df = df.sort_values("weight", ascending=False).reset_index(drop=True)
    return df

def shap_to_table(shap_list: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(shap_list)

    def split_feature(f):
        if "__" in f:
            left, right = f.split("__", 1)
            return left, right
        return f, ""

    df[["entity", "metric"]] = df["feature"].apply(lambda x: pd.Series(split_feature(x)))
    df = df[["entity", "metric", "value", "shap", "direction"]]
    df = df.sort_values("shap", key=np.abs, ascending=False).reset_index(drop=True)
    return df

def generate_user_report(regime_monthly: pd.DataFrame,
                         feat_asset_monthly: pd.DataFrame,
                         asset_master: pd.DataFrame,
                         eom: pd.Timestamp,
                         user_profile: str,
                         params: PolicyParams,
                         mu_model: MuModel,
                         assets: list[str],
                         background_months: int = 60,
                         nsamples: int = 200,
                         top_k: int = 8):
    eom = pd.to_datetime(eom)
    equity_assets = infer_equity_assets(assets, asset_master)

    st = load_state(regime_monthly, feat_asset_monthly, eom, assets)
    regime = st["regime"]

    policy_user = choose_policy(regime, user_profile)
    policy_opp = choose_policy(regime, opposite_profile(user_profile))

    x_user = state_to_X(st, user_profile, assets)
    x_opp = state_to_X(st, opposite_profile(user_profile), assets)

    w_user = policy_compute_weights(policy_user, x_user, params, mu_model, assets, equity_assets)
    w_opp = policy_compute_weights(policy_opp, x_opp, params, mu_model, assets, equity_assets)

    eoms = get_common_eoms(regime_monthly, feat_asset_monthly, assets, min_assets=len(assets))
    eoms = [t for t in eoms if t <= eom]
    eoms_bg = eoms[-background_months:] if len(eoms) > background_months else eoms

    X_bg = []
    for t in eoms_bg:
        st_bg = load_state(regime_monthly, feat_asset_monthly, t, assets)
        X_bg.append(state_to_X(st_bg, user_profile, assets))
    X_bg = np.array(X_bg, dtype=float)
    if X_bg.ndim != 2 or X_bg.shape[0] < 10:
        X_bg = np.tile(x_user.reshape(1, -1), (20, 1))

    top_user, _ = kernel_shap_explain(policy_user, x_user, X_bg, params, mu_model, assets, equity_assets,
                                      target="equity_total", nsamples=nsamples, top_k=top_k)
    top_opp, _ = kernel_shap_explain(policy_opp, x_opp, X_bg, params, mu_model, assets, equity_assets,
                                     target="equity_total", nsamples=nsamples, top_k=top_k)

    return {
        "meta": {
            "eom": str(eom.date()),
            "regime": regime,
            "profile": user_profile,
            "policy": policy_user
        },
        "portfolio_user": portfolio_to_table(w_user),
        "portfolio_opposite": portfolio_to_table(w_opp),
        "xai_user": shap_to_table(top_user),
        "xai_opposite": shap_to_table(top_opp)
    }


# =====================================================
# J) Quick Start용 진입점
# =====================================================

def run_demo(regime_monthly: pd.DataFrame,
             feat_asset_monthly: pd.DataFrame,
             asset_master: pd.DataFrame,
             demo_eom: str,
             user_profile: str,
             assets: list[str],
             background_months: int = 60,
             nsamples: int = 200,
             top_k: int = 8):
    eom = pd.to_datetime(demo_eom)

    ret_wide = load_ret_wide(feat_asset_monthly, assets)
    corr = estimate_global_corr(ret_wide, window_months=60)
    params = PolicyParams(corr=corr)

    mu_model = train_mu_model(regime_monthly, feat_asset_monthly, ret_wide, assets)

    report_user = generate_user_report(regime_monthly, feat_asset_monthly, asset_master,
                                       eom, user_profile, params, mu_model,
                                       assets=assets,
                                       background_months=background_months,
                                       nsamples=nsamples,
                                       top_k=top_k)
    report_opp = generate_user_report(regime_monthly, feat_asset_monthly, asset_master,
                                      eom, opposite_profile(user_profile), params, mu_model,
                                      assets=assets,
                                      background_months=background_months,
                                      nsamples=nsamples,
                                      top_k=top_k)
    return report_user, report_opp
