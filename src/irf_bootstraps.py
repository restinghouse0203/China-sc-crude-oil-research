# stage 2 irf bootstraps 
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import invwishart

def stage2irf(y, q_shock, nrep=20000, seed=42):
    y = np.asarray(y).reshape(-1, 1)
    q_shock = np.asarray(q_shock).reshape(-1, 1)
    t = len(q_shock)
    pp = 12

    Z = [np.ones((t - pp, 1))]
    for i in range(pp + 1):
        Z.append(q_shock[pp - i:t - i, :])
    Z = np.hstack(Z)

    y_dep = y[pp:t, :]
    bhat = np.linalg.inv(Z.T @ Z) @ Z.T @ y_dep

    irf1hat = bhat[1:, 0]
    cumirf1hat = np.cumsum(irf1hat)

    rng = np.random.default_rng(seed)
    IRF1 = np.zeros((nrep, 13))
    cumIRF1 = np.zeros((nrep, 13))
    block = 4
    y_len = len(y_dep)

    for j in range(nrep):
        yr_blocks, Zr_blocks = [], []
        n_blocks = int(np.ceil(y_len / block))
        for _ in range(n_blocks):
            pos = int(np.ceil(rng.random() * (y_len - block)))
            start = max(0, min(pos - 1, y_len - block))
            yr_blocks.append(y_dep[start:start + block, :])
            Zr_blocks.append(Z[start:start + block, :])

        yr = np.vstack(yr_blocks)[:y_len, :]
        Zr = np.vstack(Zr_blocks)[:y_len, :]

        br = np.linalg.inv(Zr.T @ Zr) @ Zr.T @ yr
        IRF1[j, :] = br[1:, 0]
        cumIRF1[j, :] = np.cumsum(IRF1[j, :])

    q16, q84 = np.quantile(IRF1, [0.16, 0.84], axis=0)
    q025, q975 = np.quantile(IRF1, [0.025, 0.975], axis=0)
    c16, c84 = np.quantile(cumIRF1, [0.16, 0.84], axis=0)
    c025, c975 = np.quantile(cumIRF1, [0.025, 0.975], axis=0)

    return {
        'irf': irf1hat,
        'irf_68': np.vstack([q16, q84]),
        'irf_95': np.vstack([q025, q975]),
        'cum': cumirf1hat,
        'cum_68': np.vstack([c16, c84]),
        'cum_95': np.vstack([c025, c975]),
    }
