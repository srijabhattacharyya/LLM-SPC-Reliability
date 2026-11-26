# Blinded rating kit

`Rater_Form.xlsx` is the form each independent rater completes: instructions, the reference answer key, a claim-by-claim scoring sheet and a per-response summary that derives the defect label (severity 2 or 3 = defective).

The master workbook holding the blinding key (code -> model, run, dataset) is **not** published here; it is held by the author until the agreement study is complete. `analysis/kappa_analysis.py` computes Cohen's kappa, quadratically weighted kappa, PABAK and bootstrap 95% intervals from that master workbook.
