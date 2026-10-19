"""Helper functions for the Bass diffusion model.

Same formulas as in the DS 223 lecture:
    F(t) = (1 - e^{-(p+q)t}) / (1 + (q/p) e^{-(p+q)t})
    f(t) = ((p+q)^2 / p) e^{-(p+q)t} / (1 + (q/p) e^{-(p+q)t})^2
    a(t) = M * f(t),   A(t) = M * F(t)
    t*   = ln(q/p) / (p+q)   (time of peak adoptions)
"""
import numpy as np
from scipy.optimize import curve_fit, brentq


def bass_F(t, p, q):
    """Cumulative share of the market that has adopted by time t."""
    e = np.exp(-(p + q) * np.asarray(t, dtype=float))
    return (1 - e) / (1 + (q / p) * e)


def bass_f(t, p, q):
    """Adoption density (share of the market adopting at time t)."""
    e = np.exp(-(p + q) * np.asarray(t, dtype=float))
    return ((p + q) ** 2 / p) * e / (1 + (q / p) * e) ** 2


def bass_a(t, M, p, q):
    """Number of adopters at time t (continuous version, like nls in R)."""
    return M * bass_f(t, p, q)


def adopters_by_period(periods, M, p, q):
    """New adopters in each period, as the difference of the cumulative curve.

    a_k = M * (F(k) - F(k-1)). This is the discrete version and its sum
    always equals the cumulative M * F(K).
    """
    k = np.asarray(periods, dtype=float)
    return M * (bass_F(k, p, q) - bass_F(k - 1, p, q))


def peak_time(p, q):
    """Time when adoptions per period are highest."""
    return np.log(q / p) / (p + q)


def fit_nls(sales):
    """Method 1: non-linear least squares on a(t) = M f(t)."""
    sales = np.asarray(sales, dtype=float)
    t = np.arange(1, len(sales) + 1)
    p0 = [sales.sum() * 1.2, 0.01, 0.5]
    params, cov = curve_fit(
        bass_a, t, sales, p0=p0,
        bounds=([sales.sum(), 1e-6, 1e-4], [sales.sum() * 20, 1.0, 3.0]),
        maxfev=20000,
    )
    se = np.sqrt(np.diag(cov))
    return dict(zip(["M", "p", "q"], params)), dict(zip(["M", "p", "q"], se))


def fit_ols(sales):
    """Method 2: Bass (1969) linear regression.

    a(t) = b0 + b1 A(t-1) + b2 A(t-1)^2, with b0 = pM, b1 = q - p, b2 = -q/M.
    """
    sales = np.asarray(sales, dtype=float)
    A_prev = np.concatenate([[0.0], np.cumsum(sales)[:-1]])
    X = np.column_stack([np.ones_like(A_prev), A_prev, A_prev ** 2])
    b0, b1, b2 = np.linalg.lstsq(X, sales, rcond=None)[0]
    # M solves b2 M^2 + b1 M + b0 = 0 (take the positive root)
    roots = np.roots([b2, b1, b0])
    M = max(r.real for r in roots if abs(r.imag) < 1e-9)
    p = b0 / M
    q = p + b1
    return {"M": M, "p": p, "q": q}, (b0, b1, b2)


def calibrate_p(first_period_adopters, M, q):
    """Find p so that the first-period adopters M*F(1) match an observed value."""
    target = first_period_adopters / M
    return brentq(lambda p: bass_F(1, p, q) - target, 1e-6, 0.999)


def r_squared(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - actual.mean()) ** 2)
    return 1 - ss_res / ss_tot
