"""Reference values for the three process datasets (preprint Section 6).

Usage: python analysis/reference_values.py [path/to/workbook.xlsx]
Default workbook path: data/Data_set_for_DMAIC.xlsx
"""
import sys
import numpy as np
import pandas as pd
from scipy import stats

PATH = sys.argv[1] if len(sys.argv) > 1 else "data/Data_set_for_DMAIC.xlsx"
x = pd.read_excel(PATH, sheet_name=None, header=None)


def describe(v):
    v = np.asarray(v, float)
    return dict(n=len(v), sum=v.sum(), mean=round(v.mean(), 4), median=np.median(v),
                sd=round(v.std(ddof=1), 4), min=v.min(), max=v.max())


print("== Forklift breakdowns ==")
f = x["1. Forklift Breakdown"].iloc[1:, :3]
f.columns = ["phase", "period", "count"]
for p, g in f.groupby("phase", sort=False):
    v = g["count"].astype(float).values
    d = describe(v)
    stat = (len(v) - 1) * v.var(ddof=1) / v.mean()
    pval = 2 * min(stats.chi2.sf(stat, len(v) - 1), stats.chi2.cdf(stat, len(v) - 1))
    print(p, d, "var/mean", round(v.var(ddof=1) / v.mean(), 2), "periods<3", int((v < 3).sum()),
          "dispersion p", round(pval, 3))
b = f[f.phase.str.contains("Baseline")]["count"].astype(float)
c = b.mean()
print("Baseline c-chart: CL", round(c, 4), "UCL", round(c + 3 * np.sqrt(c), 4), "LCL", max(0, c - 3 * np.sqrt(c)))

print("\n== Manufacturing yield ==")
y = x["2. S1_Raw data"].iloc[1:]
for p, g in y.groupby(1, sort=False):
    print(p, describe(g[7].astype(float)))

print("\n== Loan disbursement ==")
L = x["3. Data Set for Quality"].iloc[7:, :4]
L.columns = ["phase", "month", "volume", "days"]
L["phase"] = L["phase"].str.strip()
for p, g in L.groupby("phase", sort=False):
    v = g["days"].astype(float).values
    mr = np.abs(np.diff(v)).mean()
    lcl, ucl = v.mean() - 2.66 * mr, v.mean() + 2.66 * mr
    print(p, describe(v), "MRbar", round(mr, 4), "I-chart", round(lcl, 4), round(ucl, 4),
          "MR UCL", round(3.267 * mr, 4), "outside", int(((v < lcl) | (v > ucl)).sum()))
ai = L[L.phase == "A&I"]["days"].astype(float).values
print("A&I below Baseline LCL 12.8007:", int((ai < 12.8007).sum()), "of", len(ai))

print("\n== Dated reanalysis: A&I split at intervention months (rows 1, 13, 25) ==")
for i, (a, z) in enumerate([(0, 12), (12, 24), (24, 36)], 1):
    s = ai[a:z]
    mr = np.abs(np.diff(s)).mean()
    lcl, ucl = s.mean() - 2.66 * mr, s.mean() + 2.66 * mr
    print(f"Stage {i}: mean {s.mean():.2f}, limits {lcl:.2f}-{ucl:.2f}, outside {int(((s < lcl) | (s > ucl)).sum())}")
print("Corr(volume, days):", round(np.corrcoef(L.volume.astype(float), L.days.astype(float))[0, 1], 2))
