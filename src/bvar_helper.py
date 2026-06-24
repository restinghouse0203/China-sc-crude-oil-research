# code for the bvar model 
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import invwishart

def bvar_state_matrices(B_mat, n=3, p=24):
    """Convert B matrix (k x n) into intercept and companion A."""
    c = B_mat[0, :]  # intercept (n,)
    A_top = B_mat[1:, :].T  # (n, n*p)
    if p == 1:
        A_comp = A_top
    else:
        bottom = np.hstack([np.eye(n * (p - 1)), np.zeros((n * (p - 1), n))])
        A_comp = np.vstack([A_top, bottom])
    return c, A_top, A_comp


def irf_from_companion(A_comp, Sigma, n=3, p=24, h=15):
    """Cholesky-identified IRFs as (n^2, h+1) stacked by columns."""
    J = np.hstack([np.eye(n), np.zeros((n, n * p - n))])
    C = np.linalg.cholesky(Sigma).T
    comp_power = np.eye(n * p)
    irfs = []
    for _ in range(h + 1):
        resp = J @ comp_power @ J.T @ C
        irfs.append(resp.reshape(n * n, 1, order='F'))
        comp_power = comp_power @ A_comp
    return np.hstack(irfs)


def make_var_xy(y, p):
    """Build Y, X with X=[1, y_{t-1},...,y_{t-p}] consistent with notebook ordering."""
    T, n = y.shape
    Y = y[p:, :]
    X_lags = []
    for t in range(p, T):
        row = []
        for L in range(1, p + 1):
            row.extend(y[t - L, :])
        X_lags.append(row)
    X = np.column_stack([np.ones(len(X_lags)), np.asarray(X_lags)])
    return Y, X


def structural_shocks_from_bmean(y, B_mean, Sigma_mean, p=24):
    Y, X = make_var_xy(y, p)
    U = (Y - X @ B_mean).T  # n x (T-p)
    C = np.linalg.cholesky(Sigma_mean).T
    Ehat = np.linalg.solve(C, U)
    return Ehat