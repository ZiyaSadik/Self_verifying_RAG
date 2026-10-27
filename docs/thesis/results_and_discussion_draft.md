# Results and Discussion

This chapter reports the SQuAD 1.1 evaluation of six retrieval-augmented generation conditions. The figures below are taken from the saved condition summaries and from a read-only recomputation over the saved predictions. No condition was rerun for this draft. Passage judgments that have not been confirmed by a human reviewer are marked as preliminary.

## Experimental setup

The source collection is the official SQuAD 1.1 development set (10,570 questions). A reproducible sample of 500 questions was drawn with `random.Random(42)` and then sorted by the original index. Positions 0–99 are the reported test. Positions 100–499 are reserved: they are not used to fit thresholds and they are not reported as the main result. The recorded preparation manifest states that thresholds were not fit on this sample.

All six conditions use the same test questions, the same dense index, and the same generator. Retrieval uses `BAAI/bge-small-en-v1.5` with a flat inner-product index. Passages are 200-word chunks with an overlap of 40 words, and the initial retrieval returns five chunks. The generator is local `qwen2.5:3b`, with temperature 0. The claim verifier, when it runs, is `cross-encoder/nli-deberta-v3-small` on CPU. Its label order for this model is contradiction, entailment, neutral. A claim is `SUPPORTED` when the maximum entailment is at least 0.50. Otherwise it is `CONTRADICTED` when the maximum contradiction is at least 0.50 and greater than the entailment. Every other claim is `INSUFFICIENT_EVIDENCE`. The premise mode is joint: one concatenated premise of at most 320 words, plus each retrieved passage alone. Entailment and contradiction are maximised separately, so the two maxima may come from different premises. Revision is disabled. The final policy is abstention. Evidence-level contradiction is disabled. Risk weights are 0.50 for retrieval and 0.50 for evidence coverage, with contradiction and claim weights at 0. The risk bands are 0.35 and 0.60. These risk and evidence-score settings are the project defaults. They were not recalibrated on the reported test.

The six conditions differ only in which checks are enabled:

| Condition | Role | Claim verification | Re-retrieval | Revision |
|---|---|---|---|---|
| A | Retrieve five passages and generate once | No | No | No |
| B | Evidence risk check. Re-retrieve once before generation only when risk is high | No | At most once, before generation | No |
| C | Verify claims. Re-retrieve once after a failed check, then abstain if the second check also fails | Yes | At most once, after a failed check | No |
| D | Evidence risk check and claim verification | Yes | At most once. A high-risk retrieval before generation uses that budget | No |
| E | Same as D, except claim verification is skipped when risk is low | Only when risk is not low | At most once | No |
| F | Always re-retrieve once before generation, then verify claims | Yes | Once, before generation | No |

Re-retrieval adds up to three new chunks from an expanded query. The expansion appends the title and the opening words of the top passage. It does not call the generator. Claim extraction is rule-based. Only answer generation calls the language model.

## Scoring

The saved summaries score `final_answer` against `gold_answer`. In these records `gold_answer` is the first gold string. That is the first-gold exact match, token F1, and contains-gold reported below. Contains-gold is 1 when the normalised gold string occurs inside the normalised prediction.

SQuAD scores a prediction by its best match over every accepted gold string. Those max-over-gold exact-match and token-F1 values were recomputed from the saved predictions with `exact_match_max()` and `f1_score_max()`. They are not stored in the condition summaries. Any-gold contains-gold is the maximum of the existing single-string contains-gold function over the same gold strings. The source does not define a separate function for that quantity.

Each result file contains 100 rows. The identifiers are unique, contain no duplicates, and follow positions 0–99 of the prepared question file. `gold_answer` matches both the stored `answer` field and the first span in `answers`. Recomputing the first-gold metrics from the JSONL reproduces the saved summaries. For Conditions C and D the saved F1 literal and the recomputed mean differ in the final printed digit; their absolute difference is 0.

## Measured results

First-gold scores are the values stored by the experiment. Max-over-gold scores are the recomputation.

| Condition | First-gold EM | First-gold F1 | First-gold contains | Max-over-gold EM | Max-over-gold F1 | Any-gold contains |
|---|---:|---:|---:|---:|---:|---:|
| A | 0.600 | 0.716939 | 0.720 | 0.700 | 0.779900 | 0.800 |
| B | 0.600 | 0.716939 | 0.720 | 0.700 | 0.779900 | 0.800 |
| C | 0.270 | 0.341300 | 0.330 | 0.360 | 0.398070 | 0.400 |
| D | 0.270 | 0.341300 | 0.330 | 0.360 | 0.398070 | 0.400 |
| E | 0.500 | 0.611939 | 0.600 | 0.600 | 0.672043 | 0.680 |
| F | 0.250 | 0.314785 | 0.310 | 0.330 | 0.366555 | 0.370 |

The same records give the following behaviour and cost. `safe_rate` is one minus the first-gold wrong-answer rate. A wrong answer, in that definition, is a non-abstention whose prediction does not contain the first gold string. An abstention therefore raises `safe_rate`. The quantity is not a measure of verified factual correctness. `initial_all_hit` and `final_all_hit` record whether every gold document identifier appears among the retrieved chunk document identifiers. They do not measure whether the answer span was retrieved or whether a claim is entailed.

| Condition | Abstain | Answered precision | Wrong-answer rate | Safe rate | Re-retrieval | Claim verification | Revisions | Mean LLM calls | Mean latency (s) | Mean NLI pairs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 0.020 | 0.735 | 0.260 | 0.740 | 0.000 | 0.000 | 0 | 1.00 | 18.710 | 0.00 |
| B | 0.020 | 0.735 | 0.260 | 0.740 | 0.060 | 0.000 | 0 | 1.00 | 18.219 | 0.00 |
| C | 0.530 | 0.702 | 0.140 | 0.860 | 0.620 | 0.980 | 0 | 1.62 | 31.809 | 12.12 |
| D | 0.530 | 0.702 | 0.140 | 0.860 | 0.680 | 0.980 | 0 | 1.62 | 32.757 | 12.24 |
| E | 0.160 | 0.714 | 0.240 | 0.760 | 0.230 | 0.260 | 0 | 1.17 | 22.027 | 3.24 |
| F | 0.560 | 0.705 | 0.130 | 0.870 | 1.000 | 0.970 | 0 | 1.00 | 25.747 | 9.18 |

Document-identifier hit is 0.990 initially and finally for every condition. The revision rate is 0 because revision was not enabled.

Final-answer strings are identical for A and B on all 100 questions, and identical for C and D on all 100 questions. E matches A on 84 questions and C on 62. F matches A on 40 questions and C on 93.

## Comparison of the conditions

Condition A is the generation baseline. Its max-over-gold exact match is 0.700 and its max-over-gold token F1 is 0.780. It abstains on 2 of 100 questions. Its first-gold wrong-answer rate is 0.260.

Condition B adds the evidence-risk check and re-retrieves on 6 questions. That retrieval does not change any final answer relative to A, and it does not change exact match, token F1, or contains-gold. The evidence check therefore has no measured effect on answer quality for this test under the current risk thresholds.

Conditions C and D verify claims and abstain on 53 questions. Their max-over-gold exact match falls to 0.360 and their max-over-gold token F1 falls to 0.398. The first-gold wrong-answer rate falls from 0.260 to 0.140, and `safe_rate` rises from 0.740 to 0.860, because abstention is counted as safe under that definition. Among the questions that are still answered, first-gold contains-gold precision is 0.702, close to A's answered precision of 0.735. The loss in exact match is therefore concentrated in abstention rather than in a large change among the answers that remain. C re-retrieves on 62 questions and uses 1.62 generator calls on average. D re-retrieves on 68 questions and has a slightly higher mean latency and NLI-pair count, but it produces the same final answer as C on every test question. Adding the evidence-risk check to claim verification does not change the reported answers on this split.

Condition E runs the claim check on 26 questions. Its abstention rate is 0.160. Max-over-gold exact match is 0.600 and max-over-gold token F1 is 0.672, below A and above C. Mean generator use is 1.17 calls and mean latency is 22.027 seconds. Skipping verification when risk is low preserves more of the baseline score than verifying every non-abstaining answer, and it also leaves a higher first-gold wrong-answer rate than C (0.240 against 0.140).

Condition F always re-retrieves once and then verifies claims. It makes one generator call per question. It abstains on 56 questions, re-retrieves on all 100, and has the lowest max-over-gold exact match, 0.330. Its first-gold wrong-answer rate is 0.130, the lowest of the six conditions, again because more questions are abstentions. Forcing the single re-retrieval before generation does not recover the exact-match loss from claim verification.

## Claim verification in Condition C

The stored Condition C records show why exact match falls. The verifier does not compare a claim with a gold span. It compares the generated statement with the retrieved text. In joint mode it keeps the highest entailment across the constructed premises and, separately, the highest contradiction. A claim can therefore be labelled `CONTRADICTED` when one passage yields a small entailment and a different passage yields a large contradiction.

The saved round history stores verdict labels and entailment only. Contradiction is stored on the final claim record, not for each premise, and the first retrieval's passage text is not stored. Those records alone cannot show which passage produced the contradiction, and they cannot show whether the first retrieval supported the first generation.

A separate diagnostic rescored the 14 final claims from a 13-question sample against the 112 saved final passages, using the same local NLI model and the same 0.50 rule. This diagnostic did not regenerate answers. Recomputing the joint aggregate on those passages reproduced the stored verdict, entailment, and contradiction for all 14 claims. None of the 112 individual passage pairs reached entailment 0.50, so none was `SUPPORTED` on its own. On 12 of the 14 claims, the maximum entailment and the maximum contradiction came from different premises.

The passage that contains the relevant sentence is usually scored as neutral. Another passage then supplies a contradiction above 0.50, and the stored aggregate becomes `CONTRADICTED`. For example, the passage containing the 24-interception sentence has entailment 0.002, contradiction 0.001, and neutral 0.997. The stored contradiction of 0.996 comes from a different passage. The same split appears for the Normandy, 1881, and San Jose claims. The one near-threshold entailment is the KRFX passage, at 0.484, and that pair's own verdict is still `INSUFFICIENT_EVIDENCE`. Its stored `CONTRADICTED` verdict uses a contradiction of 0.984 from the Westwood One passage. Lowering the 0.50 support threshold would not accept the verbatim claims whose entailment is near zero. These pair scores do not justify a threshold change.

One final claim in the sample is factually wrong: it says Elway's last game was Super Bowl XXXII, while the saved passage says Super Bowl XXXIII. The pair formed by that claim and that passage is `INSUFFICIENT_EVIDENCE` (entailment 0.008, contradiction 0.096). The stored contradiction of 0.989 comes from a different passage. An aggregate `CONTRADICTED` label is therefore not, by itself, evidence that the relevant passage contradicted the claim.

## Preliminary passage reading

A 13-case worksheet was prepared from the questions on which Conditions A and B match a gold answer and Condition C abstains, together with the mixed-verdict, near-threshold, and wording-change cases needed to inspect the verifier. A preliminary reading of the saved final passages judged 11 of the 13 final claims to be supported by a retrieved passage while the stored verdict was not `SUPPORTED`. Two cases are different. In one, the second short answer is wrong and the passage text conflicts with that final claim. In the other, the short answer matches a gold string, but the full claim drops the passage's hedge, "believed to be," so the full claim has insufficient evidence. That reading is preliminary. It is not a confirmed human review, and a gold-matching short answer was not treated as proof that the full claim is supported. The blank review sheet remains the record to be completed by a reviewer. Until those labels are confirmed, the 11 disagreements are a hypothesis about false rejection, not a measured false-rejection rate.

## Discussion

The test separates answer quality from the decision to abstain. A and B give the same answers. Claim verification, as implemented in C, D, and F, removes many of those answers and replaces them with abstention. Because abstention increases `safe_rate` and reduces the wrong-answer rate, those two summary fields move in favour of C, D, and F even while exact match and token F1 fall. The chapter therefore reports exact match and token F1, both first-gold and max-over-gold, alongside abstention, and does not describe `safe_rate` as factual safety.

The per-premise scores locate the exact-match drop in the joint aggregation and in the NLI scores assigned to long passages. A passage can contain the claim sentence and still receive entailment near zero and neutral probability near one. An unrelated passage in the same retrieved set can receive contradiction near one. Joint verification then combines those two values. The result is a `CONTRADICTED` decision for a claim whose on-topic passage pair would have been `INSUFFICIENT_EVIDENCE`. Condition D uses that same joint verifier, so it does not isolate the decision. On this test it also does not change the final answers relative to C.

Condition E shows the cost of applying the check less often. Verifying 26 questions instead of 98 leaves max-over-gold exact match 0.10 below A and 0.24 above C. That gain comes from accepting low-risk answers without a claim check. It is not evidence that the verifier accepted those answers as supported.

## Limitations

The reported test has 100 questions. The reserved 400 questions were not used to select a threshold, and they should not be used for that purpose after seeing these results.

The saved experiment does not store per-premise probabilities, the premise responsible for the contradiction, or the first retrieval's passage text. The pair-level scores cover 13 questions and the final retrieval only. They explain the stored aggregates for those claims. They do not estimate how the first retrieval would have been scored.

The 13-case support labels are a preliminary reading. They await human confirmation. No false-rejection rate is claimed from them.

`safe_rate`, answered precision, and the wrong-answer rate use first-gold contains-gold. They are not max-over-gold exact match, and they treat abstention as a successful avoidance of a wrong answer. Document-identifier hit is not evidence that the answer span was present in a retrieved chunk.

Latency includes cached generator calls at their original recorded cost. It is the mean recorded latency in the condition summary, not a fresh uncached timing of the full test.
