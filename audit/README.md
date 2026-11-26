# Response-level audit labels

`response_labels.csv` has one row per planned response slot (3 models x 5 runs x 3 datasets = 45).

| Column | Meaning |
|---|---|
| `status` | `clean` = response present and mapped to its prompt; `absent` = no response; `ambiguous` = prompt-response mapping unresolved (data-integrity event, not a defect) |
| `defective` | 1 = at least one claim scored 2 or 3 on the severity rubric; 0 = no material defect; blank for absent/ambiguous slots |
| `severity_note` | `material` for defective responses; `minor` where a score-1 issue was recorded for that slot |
| `self_evaluated` | `yes` where the response was audited by the same ChatGPT workflow that produced it |

Notes:
- Claude Run 2 had one minor (score-1) internal count inconsistency; the original audit did not record which dataset it was in, so it is not attached to a row.
- These labels come from a single unblinded LLM-assisted audit and are provisional. Blinded two-rater labels will be added after the agreement study (preprint, Section 8).
