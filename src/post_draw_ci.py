# posterior draw for CI (historical decomposition + shock draws for stage 2)
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import invwishart
from bvar_helper import *
from irf_bootstraps import *


def posterior_draw_CI(y, B_draws, Sigma_draws, p=24, n=3, max_draws=2000):
    """Posterior credible bands for cumulative oil-price contributions by shock.

    For each posterior draw, recompute structural shocks and long-horizon IRFs,
    then build the historical decomposition used in Kilian Figure 4-style plots.

    Returns
    -------
    dict with median / 68% / 95% bands (shock x time) and raw draws.
    """
    y = np.asarray(y)
    T = y.shape[0]
    n_periods = T - p
    h_long = n_periods - 1
    irf_rows = [2, 5, 8]  # real oil price x shocks 1-3 (order='F')

    n_keep = B_draws.shape[0]
    max_draws = min(max_draws, n_keep)
    idx = np.linspace(0, n_keep - 1, max_draws, dtype=int)

    yhat_draws = np.zeros((max_draws, n, n_periods))
    Ehat_draws = np.zeros((max_draws, n, n_periods))

    for j, d in enumerate(idx):
        B_d = B_draws[d]
        S_d = Sigma_draws[d]
        Ehat_d = structural_shocks_from_bmean(y, B_d, S_d, p=p)
        Ehat_draws[j] = Ehat_d

        _, _, A_comp_d = bvar_state_matrices(B_d, n=n, p=p)
        IRF_long_d = irf_from_companion(A_comp_d, S_d, n=n, p=p, h=h_long)

        for shock in range(n):
            row = irf_rows[shock]
            psi = IRF_long_d[row, :]
            eps = Ehat_d[shock, :]
            for i in range(n_periods):
                yhat_draws[j, shock, i] = np.dot(psi[: i + 1], eps[i::-1])

    return {
        'yhat_draws': yhat_draws,
        'Ehat_draws': Ehat_draws,
        'median': np.median(yhat_draws, axis=0),
        'q68': np.quantile(yhat_draws, [0.16, 0.84], axis=0),
        'q95': np.quantile(yhat_draws, [0.025, 0.975], axis=0),
        'n_periods': n_periods,
    }


def stage2_posterior_ci(y_dep, Ehat_draws, shock_idx, nq, pp=12, h=12):
    """Posterior credible bands for stage-2 distributed-lag responses.

    Uses the same quarterly shock construction as the point estimates, but
    re-estimates the stage-2 regression for each posterior draw of shocks.
    """
    y_dep = np.asarray(y_dep).reshape(-1, 1)
    n_draws = Ehat_draws.shape[0]
    n_coef = h + 1
    irf_draws = np.zeros((n_draws, n_coef))

    for j in range(n_draws):
        q_m = Ehat_draws[j, shock_idx]
        q = np.concatenate([[(q_m[0] + q_m[1]) / 2], q_m])
        q_q = q[: 3 * nq].reshape(-1, 3).mean(axis=1).reshape(-1, 1)
        t = len(q_q)

        Z = [np.ones((t - pp, 1))]
        for lag in range(pp + 1):
            Z.append(q_q[pp - lag : t - lag, :])
        Z = np.hstack(Z)
        y_r = y_dep[pp:t, :]
        bhat = np.linalg.solve(Z.T @ Z, Z.T @ y_r)
        irf_draws[j, :] = bhat[1:, 0].ravel()

    cum_draws = np.cumsum(irf_draws, axis=1)
    q16, q84 = np.quantile(irf_draws, [0.16, 0.84], axis=0)
    q025, q975 = np.quantile(irf_draws, [0.025, 0.975], axis=0)
    c16, c84 = np.quantile(cum_draws, [0.16, 0.84], axis=0)
    c025, c975 = np.quantile(cum_draws, [0.025, 0.975], axis=0)

    return {
        'irf': np.median(irf_draws, axis=0),
        'irf_68': np.vstack([q16, q84]),
        'irf_95': np.vstack([q025, q975]),
        'cum': np.median(cum_draws, axis=0),
        'cum_68': np.vstack([c16, c84]),
        'cum_95': np.vstack([c025, c975]),
    }
