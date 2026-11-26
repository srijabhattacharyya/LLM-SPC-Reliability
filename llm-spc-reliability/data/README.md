# Process data

`Data_set_for_DMAIC.xlsx` holds the three process datasets used in the study (141 observations in total):

| Sheet | Dataset | Contents |
|---|---|---|
| `1. Forklift Breakdown` | Forklift breakdowns | Breakdowns per 15-day period, by phase (Baseline 15, Analyse & Improve 19, Control 13) |
| `2. S1_Raw data` | Manufacturing yield | % yield per production experiment, by phase (Baseline 10, Improve 8, Control 7), with raw-material and additive masses |
| `3. Data Set for Quality` | Loan disbursement | Days to disburse per month, October 2019 to June 2025, by phase (Baseline 26, Analyse & Improve 36, Control 7), a second loan column and the three intervention notes |

The models were given only the phase-labelled values (see `prompts/`). The month column and intervention placement are used only in the dated reanalysis (preprint, Section 6.4).

Run `python analysis/reference_values.py` from the repository root to recompute every reference value.
