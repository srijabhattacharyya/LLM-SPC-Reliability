"""Batch quantities, LPRI, CUSUM, EWMA, sensitivity analyses and defect-rate CIs
(preprint Sections 5.5-5.8 and 7). Usage: python analysis/monitoring.py
"""
import numpy as np
import pandas as pd
from scipy import stats

labels = pd.read_csv("audit/response_labels.csv")
K, H, LAM, L, SIGMA0 = 0.19, 0.67, 0.20, 2.7, 13.86


def batches(df, denom_observed=False):
    out = {}
    for m, g in df.groupby("model", sort=False):
        D, I = [], []
        for r in range(1, 6):
            b = g[g.run == r]
            d = int(b.defective.fillna(0).sum())
            mi = int(b.status.isin(["absent", "ambiguous"]).sum())
            n = 3 - int((b.status == "absent").sum()) if denom_observed else 3
            D.append(d / n); I.append(mi / 3)
        out[m] = (np.array(D), np.array(I))
    return out


def cusum(D, k=K):
    s, S = 0.0, []
    for x in D:
        s = max(0.0, s + x - k); S.append(s)
    return np.array(S)


def ewma(lpri, mu0=90.0):
    z, Z = mu0, []
    for x in lpri:
        z = LAM * x + (1 - LAM) * z; Z.append(z)
    t = np.arange(1, 6)
    lcl = mu0 - L * SIGMA0 * np.sqrt(LAM / (2 - LAM) * (1 - (1 - LAM) ** (2 * t)))
    return np.array(Z), lcl


def report(df, title, h=H, mu0=90.0, denom_observed=False):
    print(f"\n== {title} ==")
    for m, (D, I) in batches(df, denom_observed).items():
        lpri = 100 * (1 - 0.8 * D - 0.2 * I)
        S = cusum(D); Z, lcl = ewma(lpri, mu0)
        print(f"{m}: LPRI {np.round(lpri, 2)} mean {lpri.mean():.2f} | CUSUM {np.round(S, 3)} "
              f"signals {[t + 1 for t in range(5) if S[t] > h]} | EWMA {np.round(Z, 2)} "
              f"signals {[t + 1 for t in range(5) if Z[t] < lcl[t]]}")
    print("EWMA LCL:", np.round(lcl, 2))


report(labels, "Primary analysis")
report(labels, "Sensitivity: h = 0.40", h=0.40)
report(labels, "Sensitivity: mu0 = 92", mu0=92.0)
orig = labels.copy()
amb = orig.status == "ambiguous"
orig.loc[amb, ["status", "defective"]] = ["clean", 1]
report(orig, "Sensitivity: ambiguous Claude R3 slot counted as a defect")
report(labels, "Sensitivity: defects divided by responses received", denom_observed=True)

print("\n== Defect proportions (clean slots), exact 95% CIs ==")
clean = labels[labels.status == "clean"]
for m, g in list(clean.groupby("model", sort=False)) + [("Pooled", clean)]:
    x, n = int(g.defective.sum()), len(g)
    lo = stats.beta.ppf(0.025, x, n - x + 1) if x > 0 else 0.0
    hi = stats.beta.ppf(0.975, x + 1, n - x) if x < n else 1.0
    print(f"{m}: {x}/{n} = {x / n:.3f} (95% CI {lo:.3f}-{hi:.3f})")
