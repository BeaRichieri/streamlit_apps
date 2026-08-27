"""LuKARS 3.0 teaching implementation adapted from LuKARS3.0_Baget.ipynb.

The equations and units follow the uploaded notebook. The lower-compartment
implementation includes numerical safeguards for threshold handling, nonlinear
coefficient evaluation, time-step consistency, and flux bookkeeping.
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
    """Return the effective linear coefficient used for a power-law flux.

    The original expression is k * (h-h_threshold)**(a-1).  Evaluating this
    directly at a zero head difference can generate infinities when a < 1 and
    0**negative is encountered.  LuKARS teaching parameter ranges normally use
    a >= 1; the explicit guards below keep the routine finite at the boundary.
    """
    if k <= 0.0:
        return 0.0

    dh = h - h_threshold
    if dh <= 0.0:
        # For a linear reservoir (a = 1), the effective coefficient is k even
        # at zero storage.  For nonlinear exponents, the resulting flux is zero
        # at the threshold and a zero effective coefficient is numerically safe.
        if abs(a - 1.0) <= 1e-12:
            return k
        return 0.0

    value = k * dh ** (a - 1.0)
    if not np.isfinite(value) or value < 0.0:
        return 0.0
    return value


@njit(cache=True)
def eth(e, k, source, step, emin):
    """Exact update for one linearized reservoir over ``step`` time units."""
    if step <= 0.0:
        return max(e, emin)
    if k > 1e-15:
        eq = source / k
        return max(eq + (e - eq) * np.exp(-k * step), emin)
    return max(e + step * source, emin)


@njit(cache=True)
def _mcth_implicit_fallback(m, c, kmc, km, kc, sm, sc, step):
    """Stable backward-Euler fallback for the two-reservoir linear system."""
    a11 = 1.0 + step * (km + kmc)
    a12 = -step * kmc
    a21 = -step * kmc
    a22 = 1.0 + step * (kc + kmc)
    rhs1 = m + step * sm
    rhs2 = c + step * sc
    det = a11 * a22 - a12 * a21
    if abs(det) <= 1e-18:
        return max(m, 0.0), max(c, 0.0)
    m_next = (rhs1 * a22 - a12 * rhs2) / det
    c_next = (a11 * rhs2 - a21 * rhs1) / det
    return max(m_next, 0.0), max(c_next, 0.0)


@njit(cache=True)
def mcth(m, c, kmc, km, kc, sm, sc, step):
    """Advance matrix and conduit storages for frozen effective coefficients.

    This keeps the analytical LuKARS/KarstMod update, but explicitly handles
    the decoupled case and near-singular eigenvalue cases.  Those cases were
    previously able to create divisions by zero or discontinuous fallbacks.
    """
    if step <= 0.0:
        return max(m, 0.0), max(c, 0.0)

    # With no matrix-conduit exchange the two compartments are independent.
    # Handling this explicitly also covers M == C, where the effective kmc can
    # be exactly zero even when the parameter kMC itself is non-zero.
    if kmc <= 1e-15:
        return (
            eth(m, km, sm, step, 0.0),
            eth(c, kc, sc, step, 0.0),
        )

    # Special exact solution when there is exchange but no spring drainage.
    if km <= 1e-15 and kc <= 1e-15:
        mth = (
            (m + c) / 2.0
            + (sm + sc) * step / 2.0
            + (sm - sc) / (4.0 * kmc)
            + 0.5
            * (m - c - (sm - sc) / (2.0 * kmc))
            * np.exp(-2.0 * kmc * step)
        )
        cth = (
            (m + c) / 2.0
            + (sm + sc) * step / 2.0
            - (sm - sc) / (4.0 * kmc)
            - 0.5
            * (m - c - (sm - sc) / (2.0 * kmc))
            * np.exp(-2.0 * kmc * step)
        )
        return max(mth, 0.0), max(cth, 0.0)

    # Preserve positive physical coefficients for the stable fallback below.
    km_pos = km
    kc_pos = kc
    kmc_pos = kmc

    # Original analytical formulation uses the negative system coefficients.
    km = -km
    kc = -kc
    kmc = -kmc

    radicand = (
        (kmc + (kc + km) / 2.0) ** 2
        - (km * kmc + kc * kmc + kc * km)
    )
    # Tiny negative values can arise from roundoff although the physical
    # two-reservoir system has real eigenvalues.
    if radicand < 0.0:
        if radicand > -1e-14:
            radicand = 0.0
        else:
            return _mcth_implicit_fallback(
                m, c, kmc_pos, km_pos, kc_pos, sm, sc, step
            )

    f1 = np.sqrt(radicand)
    l1 = -(kmc + (kc + km) / 2.0) - f1
    l2 = -(kmc + (kc + km) / 2.0) + f1

    # Avoid divisions by an eigenvalue that is numerically zero.
    if abs(l1) <= 1e-14 or abs(l2) <= 1e-14:
        return _mcth_implicit_fallback(
            m, c, kmc_pos, km_pos, kc_pos, sm, sc, step
        )

    det = kmc * kmc - (l1 + kmc + km) * (l2 + kmc + kc)
    if abs(det) <= 1e-14:
        return _mcth_implicit_fallback(
            m, c, kmc_pos, km_pos, kc_pos, sm, sc, step
        )

    inv = 1.0 / det
    k100 = inv * kmc
    k101 = inv * (-l2 - kmc - kc)
    k110 = inv * (-l1 - kmc - km)
    k111 = inv * kmc

    w00 = k100 * m + k101 * c
    w01 = k110 * m + k111 * c
    weq0 = (k100 * sm + k101 * sc) / l1
    weq1 = (k110 * sm + k111 * sc) / l2

    wp0 = weq0 + (w00 - weq0) * np.exp(-l1 * step)
    wp1 = weq1 + (w01 - weq1) * np.exp(-l2 * step)

    mth = kmc * wp0 + (l2 + kmc + kc) * wp1
    cth = (l1 + kmc + km) * wp0 + kmc * wp1

    if not np.isfinite(mth) or not np.isfinite(cth):
        return _mcth_implicit_fallback(
            m, c, kmc_pos, km_pos, kc_pos, sm, sc, step
        )

    return max(mth, 0.0), max(cth, 0.0)


@njit(cache=True)
def q_bot(
    dt,
    qis,
    qhy,
    total_area,
    m0,
    c0,
    kmc,
    amc,
    c_loss,
    m_loss,
    kms,
    ams,
    kcs,
    acs,
):
    """Run the lower LuKARS matrix/conduit compartments.

    Numerical-stability changes relative to the teaching version:
    * one unified midpoint update is used instead of switching branches when
      M == C;
    * the half step is dt/2 rather than a hard-coded 0.5;
    * storage caps are applied immediately at t+1 and the overflow is recorded
      as Q_loss in the same time step;
    * spring fluxes are obtained from a dt-consistent mass balance and are
      allocated using the midpoint outlet strengths;
    * comparisons use tolerances rather than exact floating-point equality.
    """
    n = qis.shape[0]
    c = np.zeros(n, dtype=np.float64)
    m = np.zeros(n, dtype=np.float64)
    q_c_loss = np.zeros(n, dtype=np.float64)
    q_m_loss = np.zeros(n, dtype=np.float64)
    q_m_s = np.zeros(n, dtype=np.float64)
    q_c_s = np.zeros(n, dtype=np.float64)
    q_m_c = np.zeros(n, dtype=np.float64)
    q_sim = np.zeros(n, dtype=np.float64)

    if dt <= 0.0 or total_area <= 0.0:
        return (
            np.sum(qis, axis=1),
            np.sum(qhy, axis=1),
            q_c_loss,
            q_m_loss,
            q_m_s,
            q_c_s,
            q_m_c,
            q_sim,
            c,
            m,
        )

    # Start inside the admissible storage range.  Any excess initial storage is
    # treated as an immediate threshold loss at index 0.
    m_initial = max(m0, 0.0)
    c_initial = max(c0, 0.0)
    if m_initial > m_loss:
        q_m_loss[0] = (m_initial - m_loss) * total_area / dt
        m_initial = m_loss
    if c_initial > c_loss:
        q_c_loss[0] = (c_initial - c_loss) * total_area / dt
        c_initial = c_loss
    m[0] = m_initial
    c[0] = c_initial

    qem = np.sum(qis, axis=1)
    qec = np.sum(qhy, axis=1)

    # Preserved from the Baget teaching implementation: matrix recharge is
    # normalized by 70% of the total catchment area.
    sm = qem / (total_area * 0.7)
    sc = qec / total_area

    eps = 1e-14
    half_dt = 0.5 * dt

    for i in range(n - 1):
        # Effective coefficients at the beginning of the step.
        kms_i = ki_seuil(kms, ams, m[i], 0.0)
        kcs_i = ki_seuil(kcs, acs, c[i], 0.0)
        kmc_i = ki_seuil(kmc, amc, abs(m[i] - c[i]), 0.0)

        # Predictor to the middle of the time step.
        m12, c12 = mcth(
            m[i], c[i], kmc_i, kms_i, kcs_i, sm[i], sc[i], half_dt
        )
        m12 = min(max(m12, 0.0), m_loss)
        c12 = min(max(c12, 0.0), c_loss)

        # Re-evaluate nonlinear effective coefficients at the midpoint.
        kms_12 = ki_seuil(kms, ams, m12, 0.0)
        kcs_12 = ki_seuil(kcs, acs, c12, 0.0)
        kmc_12 = ki_seuil(kmc, amc, abs(m12 - c12), 0.0)

        # Corrector: integrate over the complete step using midpoint rates.
        m_raw, c_raw = mcth(
            m[i], c[i], kmc_12, kms_12, kcs_12, sm[i], sc[i], dt
        )
        m_raw = max(m_raw, 0.0)
        c_raw = max(c_raw, 0.0)

        # Apply threshold drainage immediately.  Keeping states inside their
        # admissible range prevents a one-step overshoot/clip saw-tooth.
        m_overflow = max(m_raw - m_loss, 0.0)
        c_overflow = max(c_raw - c_loss, 0.0)
        m[i + 1] = min(m_raw, m_loss)
        c[i + 1] = min(c_raw, c_loss)

        q_m_loss_depth = m_overflow / dt
        q_c_loss_depth = c_overflow / dt
        if m_overflow > 0.0:
            q_m_loss[i + 1] = q_m_loss_depth * total_area
        if c_overflow > 0.0:
            q_c_loss[i + 1] = q_c_loss_depth * total_area

        # Total spring drainage from mass conservation.  The original code
        # omitted /dt here (harmless only when dt == 1) and did not subtract
        # threshold losses, which could produce negative or zero spikes.
        d_storage_dt = (
            (m[i + 1] - m[i]) + (c[i + 1] - c[i])
        ) / dt
        spring_total = (
            sm[i]
            + sc[i]
            - d_storage_dt
            - q_m_loss_depth
            - q_c_loss_depth
        )
        if spring_total < 0.0 and spring_total > -1e-12:
            spring_total = 0.0
        spring_total = max(spring_total, 0.0)

        # Allocate the mass-balanced spring drainage between M and C using the
        # midpoint outlet strengths.  This is stable even when one outlet is
        # exactly zero (e.g. kMS = 0 in the Baget teaching parameter set).
        weight_m = max(kms_12 * m12, 0.0)
        weight_c = max(kcs_12 * c12, 0.0)
        weight_sum = weight_m + weight_c
        if spring_total > eps and weight_sum > eps:
            q_m_s[i + 1] = spring_total * weight_m / weight_sum
            q_c_s[i + 1] = spring_total - q_m_s[i + 1]
        else:
            q_m_s[i + 1] = 0.0
            q_c_s[i + 1] = 0.0

        # Matrix-to-conduit exchange from the matrix water balance.  Positive
        # values mean M -> C; negative values mean C -> M.
        q_m_c[i + 1] = (
            sm[i]
            - q_m_s[i + 1]
            - q_m_loss_depth
            - (m[i + 1] - m[i]) / dt
        )

        q_sim[i + 1] = q_m_s[i + 1] + q_c_s[i + 1]

    # Unit conversion to m3/s.  Internal q_* arrays above are equivalent
    # depth rates (mm/h), except q_*_loss which already contain mm*m2/h.
    dt_s = 3600.0
    q_c_loss = q_c_loss / dt_s / 1e3
    q_m_loss = q_m_loss / dt_s / 1e3
    q_m_s = q_m_s * total_area / (1000.0 * dt_s)
    q_c_s = q_c_s * total_area / (1000.0 * dt_s)
    q_m_c = q_m_c * total_area / (1000.0 * dt_s)
    q_sim = q_sim * total_area / (1000.0 * dt_s)

    return (
        qem,
        qec,
        q_c_loss,
        q_m_loss,
        q_m_s,
        q_c_s,
        q_m_c,
        q_sim,
        c,
        m,
    )


def run_model(sns, params):
    sns = np.asarray(sns, dtype=float)
    areas = np.asarray(params["areas"], dtype=float)
    h = len(areas); n = len(sns)
    run_up = np.zeros((3, n, h), dtype=float)
    for j in range(h):
        run_up[:, :, j] = q_up(
            params.get("dt", 1.0), sns, params.get("E0", 1.0), params.get("Qis0", 1.0),
            areas[j], params["kis"][j], params.get("Qhy0", 0.0), params["Emin"][j],
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
