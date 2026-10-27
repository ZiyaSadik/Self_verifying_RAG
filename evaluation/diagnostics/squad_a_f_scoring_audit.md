# SQuAD Conditions A–F scoring audit

Read-only recomputation. This file does not replace the saved summaries. No experiment was rerun.

Inputs:

- `data/processed/squad/questions.json` positions 0–99
- `evaluation/results/squad_cond_A.jsonl` through `squad_cond_F.jsonl`
- The matching `squad_cond_*_summary.json` files
- `exact_match()`, `f1_score()`, `contains_gold()`, `exact_match_max()`, and `f1_score_max()` in `src/evaluation/answer_metrics.py`

The saved summaries call `exact_match()`, `f1_score()`, and `contains_gold()` with `gold_answer`. In these files that field is the first gold string. `exact_match_max()` and `f1_score_max()` take the best score over every `answers[].text`. Any-gold contains-gold is the maximum of the existing `contains_gold()` over those same strings. It is not a value stored in the summaries.

## A–F comparison

| Condition | Joined rows | Saved first-gold EM | Saved first-gold F1 | Recomputed first-gold EM | Recomputed first-gold F1 | Max-over-gold EM | Max-over-gold F1 | Saved first-gold contains | Recomputed first-gold contains | Any-gold contains |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 100 | 0.6 | 0.7169392047593284 | 0.6 | 0.7169392047593284 | 0.7 | 0.7798997958923333 | 0.72 | 0.72 | 0.8 |
| B | 100 | 0.6 | 0.7169392047593284 | 0.6 | 0.7169392047593284 | 0.7 | 0.7798997958923333 | 0.72 | 0.72 | 0.8 |
| C | 100 | 0.27 | 0.34130001062013415 | 0.27 | 0.3413000106201342 | 0.36 | 0.3980701255626629 | 0.33 | 0.33 | 0.4 |
| D | 100 | 0.27 | 0.34130001062013415 | 0.27 | 0.3413000106201342 | 0.36 | 0.3980701255626629 | 0.33 | 0.33 | 0.4 |
| E | 100 | 0.5 | 0.6119392047593283 | 0.5 | 0.6119392047593283 | 0.6 | 0.6720426530351905 | 0.6 | 0.6 | 0.68 |
| F | 100 | 0.25 | 0.3147848591049826 | 0.25 | 0.3147848591049826 | 0.33 | 0.3665549740475114 | 0.31 | 0.31 | 0.37 |

Max-over-gold EM and F1 are recomputed here. They are unavailable in the original summary files. Any-gold contains is also unavailable in those files. No cell above is an estimate.

## ID checks and per-condition scores

## Condition A

- Result rows: 100
- Unique IDs: 100
- Duplicate IDs: 0
- Missing test IDs from positions 0–99: 0
- IDs outside positions 0–99: 0
- Row order equals positions 0–99: yes
- ID set equals positions 0–99 with no duplicates: yes
- Rows joined to positions 0–99: 100
- `gold_answer` differs from `questions.json` `answer`: 0
- `gold_answer` differs from `answers[0].text`: 0
- Rows missing `final_answer`: 0

Saved summary, first gold only (`final_answer` against `gold_answer`):

- EM: 0.6
- F1: 0.7169392047593284
- contains_gold: 0.72
- Summary n: 100

Recomputed from the JSONL with the same single-string functions:

- First-gold EM: 0.6
- First-gold F1: 0.7169392047593284
- First-gold contains_gold: 0.72
- Absolute gap versus the saved summary: EM 0.0, F1 0.0, contains_gold 0.0

Recomputed with `exact_match_max()` and `f1_score_max()` over every `answers[].text`:

- Max-over-gold EM: 0.7
- Max-over-gold F1: 0.7798997958923333

Contains-gold against every gold string uses the existing `contains_gold()` function and keeps the maximum. The source has no `contains_gold_max()` function, and the saved summary does not store this value.

- Any-gold contains_gold: 0.8
- Saved first-gold contains_gold: 0.72

## Condition B

- Result rows: 100
- Unique IDs: 100
- Duplicate IDs: 0
- Missing test IDs from positions 0–99: 0
- IDs outside positions 0–99: 0
- Row order equals positions 0–99: yes
- ID set equals positions 0–99 with no duplicates: yes
- Rows joined to positions 0–99: 100
- `gold_answer` differs from `questions.json` `answer`: 0
- `gold_answer` differs from `answers[0].text`: 0
- Rows missing `final_answer`: 0

Saved summary, first gold only (`final_answer` against `gold_answer`):

- EM: 0.6
- F1: 0.7169392047593284
- contains_gold: 0.72
- Summary n: 100

Recomputed from the JSONL with the same single-string functions:

- First-gold EM: 0.6
- First-gold F1: 0.7169392047593284
- First-gold contains_gold: 0.72
- Absolute gap versus the saved summary: EM 0.0, F1 0.0, contains_gold 0.0

Recomputed with `exact_match_max()` and `f1_score_max()` over every `answers[].text`:

- Max-over-gold EM: 0.7
- Max-over-gold F1: 0.7798997958923333

Contains-gold against every gold string uses the existing `contains_gold()` function and keeps the maximum. The source has no `contains_gold_max()` function, and the saved summary does not store this value.

- Any-gold contains_gold: 0.8
- Saved first-gold contains_gold: 0.72

## Condition C

- Result rows: 100
- Unique IDs: 100
- Duplicate IDs: 0
- Missing test IDs from positions 0–99: 0
- IDs outside positions 0–99: 0
- Row order equals positions 0–99: yes
- ID set equals positions 0–99 with no duplicates: yes
- Rows joined to positions 0–99: 100
- `gold_answer` differs from `questions.json` `answer`: 0
- `gold_answer` differs from `answers[0].text`: 0
- Rows missing `final_answer`: 0

Saved summary, first gold only (`final_answer` against `gold_answer`):

- EM: 0.27
- F1: 0.34130001062013415
- contains_gold: 0.33
- Summary n: 100

Recomputed from the JSONL with the same single-string functions:

- First-gold EM: 0.27
- First-gold F1: 0.3413000106201342
- First-gold contains_gold: 0.33
- Absolute gap versus the saved summary: EM 0.0, F1 0.0, contains_gold 0.0

Recomputed with `exact_match_max()` and `f1_score_max()` over every `answers[].text`:

- Max-over-gold EM: 0.36
- Max-over-gold F1: 0.3980701255626629

Contains-gold against every gold string uses the existing `contains_gold()` function and keeps the maximum. The source has no `contains_gold_max()` function, and the saved summary does not store this value.

- Any-gold contains_gold: 0.4
- Saved first-gold contains_gold: 0.33

## Condition D

- Result rows: 100
- Unique IDs: 100
- Duplicate IDs: 0
- Missing test IDs from positions 0–99: 0
- IDs outside positions 0–99: 0
- Row order equals positions 0–99: yes
- ID set equals positions 0–99 with no duplicates: yes
- Rows joined to positions 0–99: 100
- `gold_answer` differs from `questions.json` `answer`: 0
- `gold_answer` differs from `answers[0].text`: 0
- Rows missing `final_answer`: 0

Saved summary, first gold only (`final_answer` against `gold_answer`):

- EM: 0.27
- F1: 0.34130001062013415
- contains_gold: 0.33
- Summary n: 100

Recomputed from the JSONL with the same single-string functions:

- First-gold EM: 0.27
- First-gold F1: 0.3413000106201342
- First-gold contains_gold: 0.33
- Absolute gap versus the saved summary: EM 0.0, F1 0.0, contains_gold 0.0

Recomputed with `exact_match_max()` and `f1_score_max()` over every `answers[].text`:

- Max-over-gold EM: 0.36
- Max-over-gold F1: 0.3980701255626629

Contains-gold against every gold string uses the existing `contains_gold()` function and keeps the maximum. The source has no `contains_gold_max()` function, and the saved summary does not store this value.

- Any-gold contains_gold: 0.4
- Saved first-gold contains_gold: 0.33

## Condition E

- Result rows: 100
- Unique IDs: 100
- Duplicate IDs: 0
- Missing test IDs from positions 0–99: 0
- IDs outside positions 0–99: 0
- Row order equals positions 0–99: yes
- ID set equals positions 0–99 with no duplicates: yes
- Rows joined to positions 0–99: 100
- `gold_answer` differs from `questions.json` `answer`: 0
- `gold_answer` differs from `answers[0].text`: 0
- Rows missing `final_answer`: 0

Saved summary, first gold only (`final_answer` against `gold_answer`):

- EM: 0.5
- F1: 0.6119392047593283
- contains_gold: 0.6
- Summary n: 100

Recomputed from the JSONL with the same single-string functions:

- First-gold EM: 0.5
- First-gold F1: 0.6119392047593283
- First-gold contains_gold: 0.6
- Absolute gap versus the saved summary: EM 0.0, F1 0.0, contains_gold 0.0

Recomputed with `exact_match_max()` and `f1_score_max()` over every `answers[].text`:

- Max-over-gold EM: 0.6
- Max-over-gold F1: 0.6720426530351905

Contains-gold against every gold string uses the existing `contains_gold()` function and keeps the maximum. The source has no `contains_gold_max()` function, and the saved summary does not store this value.

- Any-gold contains_gold: 0.68
- Saved first-gold contains_gold: 0.6

## Condition F

- Result rows: 100
- Unique IDs: 100
- Duplicate IDs: 0
- Missing test IDs from positions 0–99: 0
- IDs outside positions 0–99: 0
- Row order equals positions 0–99: yes
- ID set equals positions 0–99 with no duplicates: yes
- Rows joined to positions 0–99: 100
- `gold_answer` differs from `questions.json` `answer`: 0
- `gold_answer` differs from `answers[0].text`: 0
- Rows missing `final_answer`: 0

Saved summary, first gold only (`final_answer` against `gold_answer`):

- EM: 0.25
- F1: 0.3147848591049826
- contains_gold: 0.31
- Summary n: 100

Recomputed from the JSONL with the same single-string functions:

- First-gold EM: 0.25
- First-gold F1: 0.3147848591049826
- First-gold contains_gold: 0.31
- Absolute gap versus the saved summary: EM 0.0, F1 0.0, contains_gold 0.0

Recomputed with `exact_match_max()` and `f1_score_max()` over every `answers[].text`:

- Max-over-gold EM: 0.33
- Max-over-gold F1: 0.3665549740475114

Contains-gold against every gold string uses the existing `contains_gold()` function and keeps the maximum. The source has no `contains_gold_max()` function, and the saved summary does not store this value.

- Any-gold contains_gold: 0.37
- Saved first-gold contains_gold: 0.31

## Consistency

No inconsistencies were found. Saved summary EM, F1, and contains_gold match a recomputation with `exact_match()`, `f1_score()`, and `contains_gold()` on `final_answer` against `gold_answer`. Every file has 100 unique IDs in positions 0–99, in that order. `gold_answer` matches both `answer` and `answers[0].text`.

## Files read

SHA-256 was computed while reading. This audit does not write these paths.

| File | Bytes | SHA-256 |
|---|---:|---|
| `squad_cond_A.jsonl` | 527916 | `e41d267a2ad61bb8a480c9010e2d1476eb501f7289764d13b9298c3d9ab2f93d` |
| `squad_cond_B.jsonl` | 661416 | `a74456591f6ac611933705e24031e5222a50c84466400114063745e918693efe` |
| `squad_cond_C.jsonl` | 829256 | `5bc2bff3ef63398d14f26cce252a1ae90099387c12909cfcd95209811027ea13` |
| `squad_cond_D.jsonl` | 994596 | `d08bb4a2925afd52fd8e9c69ff2d31b9d98a050dc13388901b0b9b500145713a` |
| `squad_cond_E.jsonl` | 751800 | `5a7874bc1e10d3d71b186f74fa14fcf7de982affd83746221504165e60c87d72` |
| `squad_cond_F.jsonl` | 1052991 | `0b3e7dd8c5bc519195e14475d7c507c8df97430e2d16802276f7bf85292abb29` |
| `squad_cond_A_summary.json` | 1912 | `66dad045f0cdb04b3440e9bb08f03079024897a0b45daf4b087204946048114a` |
| `squad_cond_B_summary.json` | 1912 | `49d99628aa71167af33d5559d6b9a9b1e4f768f0a619b3565de7966d52d9eeb3` |
| `squad_cond_C_summary.json` | 1921 | `dabf41aea100ddbcfd074df0d87ef6bf60323413ded72770e3b1ebefa6f1fbcb` |
| `squad_cond_D_summary.json` | 1919 | `5fb53f412a438d0456730d00e5312f70e7c99b32d0276554201f2a5d339b3af8` |
| `squad_cond_E_summary.json` | 1915 | `6aeec0705c17e4e969b3f4e75bc187ad862aafe8e0866198b312681bad521db0` |
| `squad_cond_F_summary.json` | 1914 | `4e0246e9787a38bc11ba36861a98e16821bbfb396182971fa0b18bddf11ca7d0` |
