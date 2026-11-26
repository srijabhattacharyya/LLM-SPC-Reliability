"""Monte Carlo average run length of the pilot CUSUM and EWMA designs (preprint Section 7.6).
Usage: python analysis/arl_simulation.py   (about a minute)
"""
import numpy as np

rng = np.random.default_rng(1)
N, MAXT = 200_000, 5000


def arl_cusum(p, k=0.19, h=0.67):
    s = np.zeros(N); rl = np.full(N, MAXT); alive = np.ones(N, bool)
    for t in range(1, MAXT + 1):
        s = np.maximum(0, s + rng.binomial(3, p, N) / 3 - k)
        hit = alive & (s > h); rl[hit] = t; alive &= ~hit
        if not alive.any():
            break
    return rl.mean()


def arl_ewma(p, mu0=90.0, lam=0.2, L=2.7, s0=13.86):
    z = np.full(N, mu0); rl = np.full(N, MAXT); alive = np.ones(N, bool)
    for t in range(1, MAXT + 1):
        z = lam * 100 * (1 - 0.8 * rng.binomial(3, p, N) / 3) + (1 - lam) * z
        lcl = mu0 - L * s0 * np.sqrt(lam / (2 - lam) * (1 - (1 - lam) ** (2 * t)))
        hit = alive & (z < lcl); rl[hit] = t; alive &= ~hit
        if not alive.any():
            break
    return rl.mean()


for p in (0.10, 0.20, 0.30):
    print(f"p={p:.2f}  CUSUM {arl_cusum(p):.1f}  EWMA(mu0=90) {arl_ewma(p):.1f}  EWMA(mu0=92) {arl_ewma(p, 92.0):.1f}")
