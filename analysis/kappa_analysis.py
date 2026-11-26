"""
Pre-registered inter-rater agreement analysis (preprint Section 6).

Usage:  python kappa_analysis.py Rating_Kit_MASTER.xlsx
Needs:  pip install openpyxl numpy

Reads only the typed-in cells (Key sheet; Ratings columns A, F, H, K), so it does not
depend on Excel having recalculated the workbook. Prints the results and writes
kappa_results.md next to the workbook.
"""
import sys, pathlib
import numpy as np
from openpyxl import load_workbook

SEED, B = 20261120, 2000

def cohen(a, b):
    a, b = np.asarray(a), np.asarray(b)
    po = np.mean(a == b); pa, pb = a.mean(), b.mean()
    pe = pa * pb + (1 - pa) * (1 - pb)
    return np.nan if pe == 1 else (po - pe) / (1 - pe)

def weighted(a, b, k=4):
    a, b = np.asarray(a, int), np.asarray(b, int)
    O = np.zeros((k, k))
    for x, y in zip(a, b): O[x, y] += 1
    n = O.sum(); i, j = np.indices((k, k)); W = 1 - (i - j) ** 2 / (k - 1) ** 2
    E = np.outer(O.sum(1), O.sum(0)) / n
    po, pe = (W * O).sum() / n, (W * E).sum() / n
    return np.nan if pe == 1 else (po - pe) / (1 - pe)

def boot(f, *cols, seed=SEED):
    rng = np.random.default_rng(seed); n = len(cols[0]); out = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        v = f(*[np.asarray(c)[idx] for c in cols])
        if not np.isnan(v): out.append(v)
    return (np.percentile(out, 2.5), np.percentile(out, 97.5)) if out else (np.nan, np.nan)

def table(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return dict(a=int(((a == 1) & (b == 1)).sum()), b=int(((a == 1) & (b == 0)).sum()),
                c=int(((a == 0) & (b == 1)).sum()), d=int(((a == 0) & (b == 0)).sum()))

def main(path):
    wb = load_workbook(path, data_only=False)
    key = {}
    for row in wb['Key'].iter_rows(min_row=2, max_row=44, values_only=True):
        if row[0]: key[row[0]] = dict(model=row[1], status=row[4], orig=row[5])
    recs = []
    for row in wb['Ratings'].iter_rows(min_row=2, max_row=44):
        code = row[0].value; sa, sb, adj = row[5].value, row[7].value, row[10].value
        if code is None or sa is None or sb is None: continue
        sa, sb = int(sa), int(sb); da, db = int(sa >= 2), int(sb >= 2)
        final = da if da == db else (int(adj) if adj is not None else None)
        recs.append(dict(code=code, sa=sa, sb=sb, da=da, db=db, final=final, **key[code]))
    if not recs:
        print("No paired ratings found yet."); return
    prim = [r for r in recs if r['status'] == 'Clean']
    L = []; p = L.append
    p(f"# Inter-rater agreement results\n\nPaired ratings: {len(recs)} (primary clean set: {len(prim)}). Bootstrap: {B} resamples, seed {SEED}.\n")
    da = [r['da'] for r in prim]; db = [r['db'] for r in prim]
    t = table(da, db); n = len(prim); po = (t['a'] + t['d']) / n
    k = cohen(da, db); lo, hi = boot(cohen, da, db)
    p("## Primary: binary defect label, Rater A vs Rater B\n")
    p(f"| | B defective | B not |\n|---|---|---|\n| A defective | {t['a']} | {t['b']} |\n| A not | {t['c']} | {t['d']} |\n")
    p(f"- Raw agreement: {po:.3f}\n- Cohen's kappa: {k:.3f} (95% CI {lo:.3f} to {hi:.3f})\n- PABAK: {2*po-1:.3f}\n- Defect prevalence: Rater A {np.mean(da):.3f}, Rater B {np.mean(db):.3f}\n")
    ok = k >= 0.60
    p(f"**Pre-specified decision rule (kappa >= 0.60): {'PASS' if ok else 'FAIL'}**\n")
    sa = [r['sa'] for r in prim]; sb = [r['sb'] for r in prim]
    kw = weighted(sa, sb); wlo, whi = boot(weighted, sa, sb)
    p(f"## Secondary: quadratic weighted kappa, max severity 0-3\n\n- Weighted kappa: {kw:.3f} (95% CI {wlo:.3f} to {whi:.3f})\n")
    if len(recs) > len(prim):
        a2 = [r['da'] for r in recs]; b2 = [r['db'] for r in recs]
        p(f"## Sensitivity: including ambiguous slot (n = {len(recs)})\n\n- Cohen's kappa: {cohen(a2, b2):.3f}\n")
    done = [r for r in prim if r['final'] is not None]
    pend = len(prim) - len(done)
    p(f"## Original ChatGPT audit vs final adjudicated label\n\n" + (f"_{pend} disagreement(s) still awaiting adjudication; they are excluded below._\n\n" if pend else ""))
    p("| Subset | n | a | b (audit 1, final 0) | c (audit 0, final 1) | d | kappa |\n|---|---|---|---|---|---|---|")
    for lab, sub in [("All", done), ("GPT (self-evaluated)", [r for r in done if r['model'] == 'GPT-5.6 Luna']),
                     ("Claude + Gemini", [r for r in done if r['model'] != 'GPT-5.6 Luna'])]:
        if not sub: continue
        o = [r['orig'] for r in sub]; f = [r['final'] for r in sub]; tt = table(o, f); kk = cohen(o, f)
        p(f"| {lab} | {len(sub)} | {tt['a']} | {tt['b']} | {tt['c']} | {tt['d']} | {'undefined' if np.isnan(kk) else f'{kk:.3f}'} |")
    p("\n## Final defect counts by model (clean set, adjudicated)\n\n| Model | Defective / rated |\n|---|---|")
    for m in ['Claude Sonnet 5.5', 'Gemini 3.8 Flash', 'GPT-5.6 Luna']:
        sub = [r for r in done if r['model'] == m]
        if sub: p(f"| {m} | {sum(r['final'] for r in sub)} / {len(sub)} |")
    out = "\n".join(L); print(out)
    pathlib.Path(path).with_name("kappa_results.md").write_text(out, encoding="utf-8")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "Rating_Kit_MASTER.xlsx")
