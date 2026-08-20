"""LuKARS 3.0 teaching implementation adapted from LuKARS3.0_Baget.ipynb.

The equations and units follow the uploaded notebook. A small indexing issue in the
notebook's Q_up loop is corrected here by iterating to n-2, because the routine
writes state values at i+1.
"""
from __future__ import annotations

import numpy as np

try:
    from numba import njit
except ImportError:  # pragma: no cover
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


@njit(cache=True)
def q_up(dt, sns, e0, qis0, area, kis, qhy0, emin, emax, alpha, khy, lhy):
    n = len(sns)
    e = np.zeros(n, dtype=np.float64)
    qis = np.zeros(n, dtype=np.float64)
    qhy = np.zeros(n, dtype=np.float64)
    e[0], qis[0], qhy[0] = e0, qis0, qhy0

    for i in range(n - 1):
        next_e = e[i] + (sns[i] - ((qhy[i] + qis[i]) / area)) * dt
        e[i + 1] = max(next_e, 0.0)
        qis[i + 1] = area * kis * e[i + 1]

        if (e[i + 1] >= emin and qhy[i] > 0.0) or (e[i + 1] >= emax and qhy[i] <= 0.0):
            denom = max(emax - emin, 1e-12)
            qhy[i + 1] = (((e[i + 1] - emin) / denom) ** alpha) * (khy / lhy) * area
        else:
            qhy[i + 1] = 0.0
    return e, qis, qhy


@njit(cache=True)
def ki_seuil(k, a, h, h_threshold):
    return max(k * (h - h_threshold) ** (a - 1.0), 0.0)


@njit(cache=True)
def eth(e, k, source, step, emin):
    if k != 0.0:
        eq = source / k
        return max(eq + (e - eq) * np.exp(-k * step), emin)
    return max(e + step * source, emin)


@njit(cache=True)
def mcth(m, c, kmc, km, kc, sm, sc, step):
    if km == 0.0 and kc == 0.0:
        if kmc == 0.0:
            return m, c
        mth = (m+c)/2 + (sm+sc)*step/2 + (sm-sc)/(4*kmc) + 0.5*(m-c-(sm-sc)/(2*kmc))*np.exp(-2*kmc*step)
        cth = (m+c)/2 + (sm+sc)*step/2 - (sm-sc)/(4*kmc) - 0.5*(m-c-(sm-sc)/(2*kmc))*np.exp(-2*kmc*step)
        return max(mth, 0.0), max(cth, 0.0)

    km, kc, kmc = -km, -kc, -kmc
    f1 = np.sqrt((kmc + (kc+km)/2) ** 2 - (km*kmc + kc*kmc + kc*km))
    l1 = -(kmc + (kc+km)/2) - f1
    l2 = -(kmc + (kc+km)/2) + f1
    det = kmc*kmc - (l1+kmc+km)*(l2+kmc+kc)
    if abs(det) < 1e-15:
        return max(m + sm*step, 0.0), max(c + sc*step, 0.0)
    inv = 1.0 / det
    k100, k101 = inv*kmc, inv*(-l2-kmc-kc)
    k110, k111 = inv*(-l1-kmc-km), inv*kmc
    w00, w01 = k100*m + k101*c, k110*m + k111*c
    weq0, weq1 = (k100*sm+k101*sc)/l1, (k110*sm+k111*sc)/l2
    wp0 = weq0 + (w00-weq0)*np.exp(-l1*step)
    wp1 = weq1 + (w01-weq1)*np.exp(-l2*step)
    return max(kmc*wp0 + (l2+kmc+kc)*wp1, 0.0), max((l1+kmc+km)*wp0 + kmc*wp1, 0.0)


@njit(cache=True)
def q_bot(dt, qis, qhy, total_area, m0, c0, kmc, amc, c_loss, m_loss, kms, ams, kcs, acs):
    n = qis.shape[0]
    c = np.zeros(n); m = np.zeros(n)
    q_c_loss = np.zeros(n); q_m_loss = np.zeros(n)
    q_m_s = np.zeros(n); q_c_s = np.zeros(n); q_m_c = np.zeros(n); q_sim = np.zeros(n)
    m[0], c[0] = m0, c0
    qem = np.sum(qis, axis=1); qec = np.sum(qhy, axis=1)
    # Preserved from the Baget notebook: matrix recharge is normalized by 70% of total area.
    sm = qem / (total_area * 0.7)
    sc = qec / total_area

    for i in range(n - 1):
        if kmc == 0.0 or m[i] == c[i]:
            if c[i] > c_loss:
                q_c_loss[i] = (c[i] - c_loss) * total_area / dt; c[i] = c_loss
            if m[i] > m_loss:
                q_m_loss[i] = (m[i] - m_loss) * total_area / dt; m[i] = m_loss
            kmsi = ki_seuil(kms, ams, m[i], 0.0)
            m12 = min(eth(m[i], kmsi, sm[i], 0.5, 0.0), m_loss)
            kmsi = ki_seuil(kms, ams, m12, 0.0)
            m[i+1] = min(eth(m[i], kmsi, sm[i], dt, 0.0), m_loss)
            q_m_s[i+1] = max(sm[i] + (m[i]-m[i+1])/dt, 0.0)
            kcsi = ki_seuil(kcs, acs, c[i], 0.0)
            c12 = min(eth(c[i], kcsi, sc[i], 0.5, 0.0), c_loss)
            kcsi = ki_seuil(kcs, acs, c12, 0.0)
            c[i+1] = min(eth(c[i], kcsi, sc[i], dt, 0.0), c_loss)
            q_c_s[i+1] = max(sc[i] + (c[i]-c[i+1])/dt, 0.0)
        else:
            if m[i] > m_loss:
                q_m_loss[i] = (m[i]-m_loss)*total_area/dt; m[i] = m_loss
            if c[i] > c_loss:
                q_c_loss[i] = (c[i]-c_loss)*total_area/dt; c[i] = c_loss
            kmsi = ki_seuil(kms, ams, m[i], 0.0)
            kcsi = ki_seuil(kcs, acs, c[i], 0.0)
            kmci = ki_seuil(kmc, amc, abs(m[i]-c[i]), 0.0)
            m12, c12 = mcth(m[i], c[i], kmci, kmsi, kcsi, sm[i], sc[i], 0.5)
            m12, c12 = min(m12, m_loss), min(c12, c_loss)
            kmsi = ki_seuil(kms, ams, m12, 0.0)
            kcsi = ki_seuil(kcs, acs, c12, 0.0)
            kmci = ki_seuil(kmc, amc, abs(m12-c12), 0.0)
            m[i+1], c[i+1] = mcth(m[i], c[i], kmci, kmsi, kcsi, sm[i], sc[i], dt)
            qmscs = -(m[i+1]-m[i]) - (c[i+1]-c[i]) + sm[i] + sc[i]
            denom = kmsi*(m[i]+m[i+1]) + kcsi*(c[i]+c[i+1])
            if qmscs != 0.0 and denom != 0.0:
                q_m_s[i+1] = qmscs * (kmsi*(m[i]+m[i+1])) / denom
                q_c_s[i+1] = qmscs - q_m_s[i+1]
            q_m_c[i+1] = (m[i]-m[i+1])/dt + sm[i] - q_m_s[i+1]
        q_sim[i+1] = max(q_m_s[i+1] + q_c_s[i+1], 0.0)

    dt_s = 3600.0
    q_c_loss = q_c_loss / dt_s / 1e3
    q_m_loss = q_m_loss / dt_s / 1e3
    q_m_s = q_m_s * total_area / (1000.0*dt_s)
    q_c_s = q_c_s * total_area / (1000.0*dt_s)
    q_m_c = q_m_c * total_area / (1000.0*dt_s)
    q_sim = q_sim * total_area / (1000.0*dt_s)
    return qem, qec, q_c_loss, q_m_loss, q_m_s, q_c_s, q_m_c, q_sim, c, m


def run_model(sns, params):
    sns = np.asarray(sns, dtype=float)
    areas = np.asarray(params["areas"], dtype=float)
    h = len(areas); n = len(sns)
    run_up = np.zeros((3, n, h), dtype=float)
    for j in range(h):
        run_up[:, :, j] = q_up(
            params.get("dt", 1.0), sns, params.get("E0", 1.0), params.get("Qis0", 1.0),
            areas[j], params["kis"][j], params.get("Qhy0", 1.0), params["Emin"][j],
            params["Emax"][j], params["alpha"][j], params["khy"][j], params["lhy"][j]
        )
    bot = q_bot(params.get("dt", 1.0), run_up[1], run_up[2], params["TotalArea"],
                params.get("M0", 1.0), params.get("C0", 0.5), params["kMC"], params["aMC"],
                params["C_loss"], params["M_loss"], params["kMS"], params["aMS"],
                params["kCS"], params["aCS"])
    run_up[1:] = run_up[1:] / 3600.0 / 1e3
    return run_up, np.asarray(bot)


def metrics(obs, sim):
    obs = np.asarray(obs, dtype=float); sim = np.asarray(sim, dtype=float)
    mask = np.isfinite(obs) & np.isfinite(sim)
    obs, sim = obs[mask], sim[mask]
    if len(obs) < 2:
        return {"NSE": np.nan, "KGE": np.nan, "RMSE": np.nan, "Bias": np.nan}
    denom = np.sum((obs - np.mean(obs))**2)
    nse = 1.0 - np.sum((obs-sim)**2)/denom if denom > 0 else np.nan
    r = np.corrcoef(obs, sim)[0,1] if np.std(obs)>0 and np.std(sim)>0 else np.nan
    alpha = np.std(sim)/np.std(obs) if np.std(obs)>0 else np.nan
    beta = np.mean(sim)/np.mean(obs) if np.mean(obs)!=0 else np.nan
    kge = 1.0 - np.sqrt((r-1)**2 + (alpha-1)**2 + (beta-1)**2) if np.isfinite(r+alpha+beta) else np.nan
    return {"NSE": nse, "KGE": kge, "RMSE": np.sqrt(np.mean((obs-sim)**2)), "Bias": np.mean(sim-obs)}
