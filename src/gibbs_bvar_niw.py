# Gibbs sampler for Bayesian VAR model with NIW prior
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import invwishart
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.api import VAR
from statsmodels.stats.diagnostic import acorr_ljungbox

def make_var_regressors(y, p):
    T, n = y.shape
    Y = y[p:, :]
    X_lags = []
    for t in range(p, T):
        row = []
        for L in range(1, p + 1):
            row.extend(y[t - L, :])
        X_lags.append(row)
    X_lags = np.asarray(X_lags)
    X = np.column_stack([np.ones(X_lags.shape[0]), X_lags])
    return Y, X

def draw_matrix_normal(M, V, Sigma, rng):
    k, n = M.shape
    Lv = np.linalg.cholesky(V)
    Ls = np.linalg.cholesky(Sigma)
    Z = rng.standard_normal((k, n))
    return M + Lv @ Z @ Ls.T
def gibbs_bvar_niw(y, p=24, n_draws=12000, burn=2000, seed=42):
    rng = np.random.default_rng(seed)
    Y, X = make_var_regressors(y, p)
    T_eff, n = Y.shape
    k = X.shape[1]

    # NIW prior hyperparameters
    B0 = np.zeros((k, n)) # starting point of the draw is 0
    V0 = np.eye(k) * 10.0 # variance of the prior is 10 %*% I
    V0_inv = np.linalg.inv(V0)
    nu0 = n + 2 # degrees of freedom of the prior
    S0 = np.eye(n) # scale matrix of the prior

    # OLS initialization
    B_ols = np.linalg.inv(X.T @ X) @ (X.T @ Y)
    E_ols = Y - X @ B_ols
    Sigma = (E_ols.T @ E_ols) / T_eff
    B = B_ols.copy()

    keep = n_draws - burn
    B_draws = np.zeros((keep, k, n))
    Sigma_draws = np.zeros((keep, n, n))
    B_trace = np.zeros((n_draws, 4))
    S_trace = np.zeros((n_draws, n))

    XtX = X.T @ X
    XtY = X.T @ Y

    for it in range(n_draws):
        Vn = np.linalg.inv(V0_inv + XtX)
        Bn = Vn @ (V0_inv @ B0 + XtY)
        B = draw_matrix_normal(Bn, Vn, Sigma, rng)

        E = Y - X @ B
        diff = B - B0
        Sn = S0 + E.T @ E + diff.T @ V0_inv @ diff
        nun = nu0 + T_eff + k
        Sigma = invwishart.rvs(df=nun, scale=Sn, random_state=rng)

        B_trace[it, :] = [B[0,0], B[1,0], B[1,1], B[2,2]]
        S_trace[it, :] = np.diag(Sigma)

        if it >= burn:
            j = it - burn
            B_draws[j] = B
            Sigma_draws[j] = Sigma

    out = {
        'Y': Y, 'X': X,
        'B_draws': B_draws,
        'Sigma_draws': Sigma_draws,
        'B_mean': B_draws.mean(axis=0),
        'Sigma_mean': Sigma_draws.mean(axis=0),
        'B_trace': B_trace,
        'S_trace': S_trace
    }
    return out