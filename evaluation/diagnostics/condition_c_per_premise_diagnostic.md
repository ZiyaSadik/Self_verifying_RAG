# Condition C per-premise diagnostic

**New pair-level diagnostic. This file is not part of the Condition C experiment, and it does not confirm a false rejection.**

A person still has to confirm the claim judgments in `evaluation/diagnostics/condition_c_review_summary.md`. Gold-answer overlap is not used here. The first retrieval's passage text is not in `squad_cond_C.jsonl`, so none of these scores describe that retrieval.

Sources read, and not modified:

- `evaluation/results/squad_cond_C.jsonl`
- `src/agents/nli.py` (`NLIScorer.score`)
- `src/agents/claim_verifier.py` (`ClaimVerifier._premises`, `ClaimVerifier._verdict`)
- `evaluation/diagnostics/condition_c_manual_review_13.md` and `condition_c_review_summary.md` for the 13 question IDs and the preliminary reading

Local model: `cross-encoder/nli-deberta-v3-small` on CPU. Label columns used by `NLIScorer._label_index`: entailment=1, neutral=2, contradiction=0. No Ollama call. No answer was regenerated.

Scoring calls in this run: 126.

## How the stored verifier aggregates premises

Condition C used joint mode and thresholds 0.50 / 0.50. For one claim, `ClaimVerifier._premises` builds:

1. One constructed premise: the saved passage strings joined in order and cut at 320 words.
2. One premise per saved passage, each passage alone.

`ClaimVerifier.verify` then scores every premise against the claim. It keeps the maximum entailment and, separately, the maximum contradiction. Those two maxima may come from different premises. `_verdict` checks support first: entailment at least 0.50 returns `SUPPORTED`. Otherwise contradiction at least 0.50 and greater than entailment returns `CONTRADICTED`. Otherwise the verdict is `INSUFFICIENT_EVIDENCE`.

The stored `claim_results` record only those two maxima, the verdict, and an explanation. They do not record neutral probability, each premise's scores, or which premise supplied the contradiction.

The pair verdicts below apply that same `_verdict` function to one passage at a time. A pair verdict can be `SUPPORTED` while the stored aggregate is `CONTRADICTED`, because the aggregate's contradiction can come from another premise. That comparison is a diagnostic observation. It is not a confirmed false rejection.

## Cross-case counts

- Claims scored: 14
- Claim–passage pairs scored: 112
- Pairs whose own verdict differs from that claim's stored aggregate verdict: 49
- Claims whose recomputed joint aggregate matches the stored verdict and both scores within 1e-6: 14 of 14
- Claims whose recomputed joint aggregate is `SUPPORTED`: 0
- Claims where the maximum entailment and the maximum contradiction come from different premises in the recomputed joint list: 12 of 14
- Claims with at least one individual passage verdict of `SUPPORTED` while the stored aggregate is not `SUPPORTED`: 0

| Case | Question ID | Claim | Stored aggregate | Recomputed joint aggregate | Scores match stored? | Maxima from different premises? | Any passage pair `SUPPORTED`? | Max-entailment premise | Max-contradiction premise |
|---|---|---:|---|---|---|---|---|---|---|
| 1 | `56bebbbf3aeaaa14008c9317` | 1 | `INSUFFICIENT_EVIDENCE` | `INSUFFICIENT_EVIDENCE` | yes | yes | no | Passage 5 | joint premise attributed to passages 1, 2, 3, 4, 5 |
| 2 | `56d71d150d65d2140019836f` | 1 | `INSUFFICIENT_EVIDENCE` | `INSUFFICIENT_EVIDENCE` | yes | no | no | Passage 1 | Passage 1 |
| 3 | `56bf717d3aeaaa14008c9639` | 1 | `INSUFFICIENT_EVIDENCE` | `INSUFFICIENT_EVIDENCE` | yes | yes | no | Passage 1 | Passage 2 |
| 4 | `56de1728cffd8e1900b4b5d7` | 1 | `CONTRADICTED` | `CONTRADICTED` | yes | no | no | Passage 1 | Passage 1 |
| 4 | `56de1728cffd8e1900b4b5d7` | 2 | `INSUFFICIENT_EVIDENCE` | `INSUFFICIENT_EVIDENCE` | yes | yes | no | Passage 1 | joint premise attributed to passages 1, 2, 3, 4, 5 |
| 5 | `56bec5233aeaaa14008c93cf` | 1 | `CONTRADICTED` | `CONTRADICTED` | yes | yes | no | Passage 1 | Passage 6 |
| 6 | `56bf48cc3aeaaa14008c95ab` | 1 | `CONTRADICTED` | `CONTRADICTED` | yes | yes | no | Passage 1 | Passage 3 |
| 7 | `57335c20d058e614000b58f9` | 1 | `CONTRADICTED` | `CONTRADICTED` | yes | yes | no | Passage 2 | Passage 8 |
| 8 | `56d6f3500d65d21400198290` | 1 | `CONTRADICTED` | `CONTRADICTED` | yes | yes | no | joint premise attributed to passages 1, 2, 3, 4, 5 | Passage 2 |
| 9 | `56de15dbcffd8e1900b4b5ca` | 1 | `CONTRADICTED` | `CONTRADICTED` | yes | yes | no | Passage 8 | Passage 4 |
| 10 | `56e0d402231d4119001ac3fc` | 1 | `CONTRADICTED` | `CONTRADICTED` | yes | yes | no | joint premise attributed to passages 1, 2, 3, 4, 5 | Passage 3 |
| 11 | `56be8e613aeaaa14008c90d2` | 1 | `CONTRADICTED` | `CONTRADICTED` | yes | yes | no | Passage 1 | Passage 4 |
| 12 | `56bebde53aeaaa14008c9338` | 1 | `CONTRADICTED` | `CONTRADICTED` | yes | yes | no | Passage 2 | Passage 7 |
| 13 | `56e1ded7cd28a01900c67bd6` | 1 | `CONTRADICTED` | `CONTRADICTED` | yes | yes | no | Passage 4 | Passage 6 |

## Missing data and checks

- Round-0 premises and round-0 contradiction scores are not in the JSONL. This file does not estimate them.
- `history` verification events store verdict labels and entailment rounded to three decimals. They are not reused as pair scores.
- Passage text is the saved `contexts` string, which is the same title-prefixed string `_ctx` passed to the verifier. Chunk IDs are `retrieved_chunk_ids` in the same order, when that list is present and aligned.

Checks: all 13 IDs were present; every scored question had final claims and final contexts; chunk-id lists aligned with contexts; the last `extract_claims` list matched `claim_results`.

## Reading the pair tables

`Differs from stored aggregate?` compares that one pair's verdict with the verdict stored for the whole claim. It does not say the stored verdict was wrong. The role column names a premise only when this recomputation finds that the joint-mode maximum falls on it. The recomputed scores match the stored scores on every claim below, so those roles are the premises that produce the stored maxima.

## What the pair scores show

None of the 112 passage pairs reaches entailment 0.50. The highest passage entailment is 0.484 on case 5, passage 1, and that pair's own verdict is `INSUFFICIENT_EVIDENCE` because its contradiction is 0.067. The stored `CONTRADICTED` verdict for that claim uses this entailment together with passage 6's contradiction of 0.984. Passage 6 is the Westwood One broadcast passage.

On 12 of 14 claims, the maximum entailment and the maximum contradiction come from different premises. For the stored `CONTRADICTED` claims other than case 4's first claim, the contradiction above 0.50 comes from a passage other than the passage with the highest entailment. The on-topic passage is usually scored as neutral. Examples from the tables:

- Case 8 passage 1 contains the 24-interception sentence. Its pair scores are entailment 0.002, contradiction 0.001, neutral 0.997, verdict `INSUFFICIENT_EVIDENCE`. The stored contradiction 0.996 is passage 2.
- Case 9 passage 1 contains the Ethelred sentence. Its pair scores are entailment 0.001, contradiction 0.001, neutral 0.998, verdict `INSUFFICIENT_EVIDENCE`. The stored contradiction 0.999 is passage 4.
- Case 10 passage 1 contains the 1881 sentence. Its pair scores are entailment 0.000, contradiction 0.009, neutral 0.991, verdict `INSUFFICIENT_EVIDENCE`. The stored contradiction 1.000 is passage 3.
- Case 12 passage 2 contains "at SAP Center in San Jose". Its pair scores are entailment 0.127, contradiction 0.001, neutral 0.872, verdict `INSUFFICIENT_EVIDENCE`. The stored contradiction 0.999 is passage 7.
- Case 6 passage 1 states that Elway's last game was Super Bowl XXXIII. The final claim says Super Bowl XXXII. That pair is still `INSUFFICIENT_EVIDENCE` (entailment 0.008, contradiction 0.096, neutral 0.896). The stored contradiction 0.989 is passage 3.

Case 2 and case 4's first claim are the two claims whose maxima fall on the same premise. Case 2's on-topic passage has entailment 0.223 and neutral 0.761, so both the pair and the stored aggregate are `INSUFFICIENT_EVIDENCE`. Case 4's first claim is `CONTRADICTED` by the same passage that contains the quoted sentence (entailment 0.006, contradiction 0.962).

`NLIScorer` uses `max_length` 512. A long premise can be truncated before scoring. Several relevant sentences occur at the start of their passage and still receive entailment near zero, so truncation of the passage ending does not account for those pair scores. This file does not treat any row as a confirmed false rejection.

## Case 1

- Question ID: `56bebbbf3aeaaa14008c9317`
- Question: Who is the NFL's vice president of brand and creative?
- Saved final passages: 8
- Chunk identifiers stored: yes
- First-retrieval passage text: not stored. No row below uses it.

### Claim 1

```text
Jaime Weston is the NFL's vice president of brand and creative
```

Stored aggregate result from `squad_cond_C.jsonl` `claim_results`:

- Verdict `INSUFFICIENT_EVIDENCE`; entailment 0.001452; contradiction 0.314451; uncertain `False`.
- Neutral probability: not stored. Per-premise probabilities: not stored. The premise that supplied each maximum: not stored.

Recomputed aggregate on these saved final passages, using `ClaimVerifier._premises` in joint mode and `ClaimVerifier._verdict` at 0.50. This recomputation is part of this diagnostic. It is not a new experiment result.

- Verdict `INSUFFICIENT_EVIDENCE`; entailment 0.001452; contradiction 0.314451; confidence 0.685549.
- Maximum entailment is premise index 5 (Passage 5).
- Maximum contradiction is premise index 0 (joint premise attributed to passages 1, 2, 3, 4, 5).
- Those two maxima come from different premises: yes.
- Recomputed aggregate matches the stored verdict and both scores within 1e-6: yes.

Pair-level rows use one saved final passage as the premise and this claim as the hypothesis. The verdict column applies the same 0.50 rule to that pair alone. It is not the verdict stored by Condition C.

| Passage | Chunk ID | Entailment | Contradiction | Neutral | Pair verdict | Differs from stored aggregate? | Role in recomputed aggregate |
|---|---|---:|---:|---:|---|---|---|
| P1 | `super_bowl_50-6b0af9df::c0` | 0.000191 | 0.001348 | 0.998462 | `INSUFFICIENT_EVIDENCE` | No |  |
| P2 | `super_bowl_50-948ae07b::c0` | 0.000111 | 0.007055 | 0.992834 | `INSUFFICIENT_EVIDENCE` | No |  |
| P3 | `super_bowl_50-c2f707a5::c0` | 0.000111 | 0.000905 | 0.998984 | `INSUFFICIENT_EVIDENCE` | No |  |
| P4 | `super_bowl_50-f1b96eb2::c0` | 0.000435 | 0.030165 | 0.969400 | `INSUFFICIENT_EVIDENCE` | No |  |
| P5 | `super_bowl_50-49dbe46e::c0` | 0.001452 | 0.006995 | 0.991553 | `INSUFFICIENT_EVIDENCE` | No | max entailment in the joint premise list |
| P6 | `super_bowl_50-aad58c5e::c0` | 0.000233 | 0.006729 | 0.993038 | `INSUFFICIENT_EVIDENCE` | No |  |
| P7 | `super_bowl_50-bcf54c0b::c0` | 0.000158 | 0.002154 | 0.997688 | `INSUFFICIENT_EVIDENCE` | No |  |
| P8 | `super_bowl_50-a533c800::c0` | 0.000399 | 0.126602 | 0.872999 | `INSUFFICIENT_EVIDENCE` | No |  |

Verifier-constructed joint premise, not a retrieved passage: first 320 words of the saved final passages joined in order, capped at 320 words. Pair verdict on this constructed premise alone: `INSUFFICIENT_EVIDENCE` (entailment 0.000737, contradiction 0.314451, neutral 0.684812). This pair verdict differs from the stored aggregate: no.

```text
Super_Bowl_50: Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24–10 to earn their third Super Bowl title. The game was played on February 7, 2016, at Levi's Stadium in the San Francisco Bay Area at Santa Clara, California. As this was the 50th Super Bowl, the league emphasized the "golden anniversary" with various gold-themed initiatives, as well as temporarily suspending the tradition of naming each Super Bowl game with Roman numerals (under which the game would have been known as "Super Bowl L"), so that the logo could prominently feature the Arabic numerals 50. Super_Bowl_50: In early 2012, NFL Commissioner Roger Goodell stated that the league planned to make the 50th Super Bowl "spectacular" and that it would be "an important game for us as a league". Super_Bowl_50: For the first time, the Super Bowl 50 Host Committee and the NFL have openly sought disabled veteran and lesbian, gay, bisexual and transgender-owned businesses in Business Connect, the Super Bowl program that provides local companies with contracting opportunities in and around the Super Bowl. The host committee has already raised over $40 million through sponsors including Apple, Google, Yahoo!, Intel, Gap, Chevron, and Dignity Health. Super_Bowl_50: The Panthers finished the regular season with a 15–1 record, and quarterback Cam Newton was named the NFL Most Valuable Player (MVP). They defeated the Arizona Cardinals 49–15 in the NFC Championship Game and advanced to their second Super Bowl appearance since the franchise was founded in 1995. The Broncos finished the regular season with a 12–4 record, and denied the New England Patriots a chance to defend their title from Super Bowl XLIX by defeating them 20–18 in the AFC Championship Game. They joined the Patriots, Dallas Cowboys, and Pittsburgh Steelers as one
```

### Exact saved final passages

These strings are the Condition C `contexts` field. Passage numbers match the table above.

#### Passage 1

- Chunk ID: `super_bowl_50-6b0af9df::c0`

```text
Super_Bowl_50: Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24–10 to earn their third Super Bowl title. The game was played on February 7, 2016, at Levi's Stadium in the San Francisco Bay Area at Santa Clara, California. As this was the 50th Super Bowl, the league emphasized the "golden anniversary" with various gold-themed initiatives, as well as temporarily suspending the tradition of naming each Super Bowl game with Roman numerals (under which the game would have been known as "Super Bowl L"), so that the logo could prominently feature the Arabic numerals 50.
```

#### Passage 2

- Chunk ID: `super_bowl_50-948ae07b::c0`

```text
Super_Bowl_50: In early 2012, NFL Commissioner Roger Goodell stated that the league planned to make the 50th Super Bowl "spectacular" and that it would be "an important game for us as a league".
```

#### Passage 3

- Chunk ID: `super_bowl_50-c2f707a5::c0`

```text
Super_Bowl_50: For the first time, the Super Bowl 50 Host Committee and the NFL have openly sought disabled veteran and lesbian, gay, bisexual and transgender-owned businesses in Business Connect, the Super Bowl program that provides local companies with contracting opportunities in and around the Super Bowl. The host committee has already raised over $40 million through sponsors including Apple, Google, Yahoo!, Intel, Gap, Chevron, and Dignity Health.
```

#### Passage 4

- Chunk ID: `super_bowl_50-f1b96eb2::c0`

```text
Super_Bowl_50: The Panthers finished the regular season with a 15–1 record, and quarterback Cam Newton was named the NFL Most Valuable Player (MVP). They defeated the Arizona Cardinals 49–15 in the NFC Championship Game and advanced to their second Super Bowl appearance since the franchise was founded in 1995. The Broncos finished the regular season with a 12–4 record, and denied the New England Patriots a chance to defend their title from Super Bowl XLIX by defeating them 20–18 in the AFC Championship Game. They joined the Patriots, Dallas Cowboys, and Pittsburgh Steelers as one of four teams that have made eight appearances in the Super Bowl.
```

#### Passage 5

- Chunk ID: `super_bowl_50-49dbe46e::c0`

```text
Super_Bowl_50: On June 4, 2014, the NFL announced that the practice of branding Super Bowl games with Roman numerals, a practice established at Super Bowl V, would be temporarily suspended, and that the game would be named using Arabic numerals as Super Bowl 50 as opposed to Super Bowl L. The use of Roman numerals will be reinstated for Super Bowl LI. Jaime Weston, the league's vice president of brand and creative, explained that a primary reason for the change was the difficulty of designing an aesthetically pleasing logo with the letter "L" using the standardized logo template introduced at Super Bowl XLV. The logo also deviates from the template by featuring large numerals, colored in gold, behind the Vince Lombardi Trophy, instead of underneath and in silver as in the standard logo.
```

#### Passage 6

- Chunk ID: `super_bowl_50-aad58c5e::c0`

```text
Super_Bowl_50: For the third straight season, the number one seeds from both conferences met in the Super Bowl. The Carolina Panthers became one of only ten teams to have completed a regular season with only one loss, and one of only six teams to have acquired a 15–1 record, while the Denver Broncos became one of four teams to have made eight appearances in the Super Bowl. The Broncos made their second Super Bowl appearance in three years, having reached Super Bowl XLVIII, while the Panthers made their second Super Bowl appearance in franchise history, their other appearance being Super Bowl XXXVIII. Coincidentally, both teams were coached by John Fox in their last Super Bowl appearance prior to Super Bowl 50.
```

#### Passage 7

- Chunk ID: `super_bowl_50-bcf54c0b::c0`

```text
Super_Bowl_50: After each team punted, Panthers quarterback Cam Newton appeared to complete a 24-yard pass Jerricho Cotchery, but the call was ruled an incompletion and upheld after a replay challenge. CBS analyst and retired referee Mike Carey stated he disagreed with the call and felt the review clearly showed the pass was complete. A few plays later, on 3rd-and-10 from the 15-yard line, linebacker Von Miller knocked the ball out of Newton's hands while sacking him, and Malik Jackson recovered it in the end zone for a Broncos touchdown, giving the team a 10–0 lead. This was the first fumble return touchdown in a Super Bowl since Super Bowl XXVIII at the end of the 1993 season.
```

#### Passage 8

- Chunk ID: `super_bowl_50-a533c800::c0`

```text
Super_Bowl_50: The Panthers seemed primed to score on their opening drive of the second half when Newton completed a 45-yard pass to Ted Ginn Jr. on the Denver 35-yard line on their second offensive play. But the Broncos defense halted the drive on the 26-yard line, and it ended with no points when Graham Gano hit the uprights on a 44-yard field goal attempt. After the miss, Manning completed a pair of passes to Emmanuel Sanders for gains of 25 and 22 yards, setting up McManus' 33-yard field goal that gave the Broncos a 16–7 lead. Carolina got off to another strong start after the kickoff, with Newton completing a 42-yard pass to Corey Brown. But once again they came up empty, this time as a result of a Newton pass that bounced off the hands of Ginn and was intercepted by safety T. J. Ward. Ward fumbled the ball during the return, but Trevathan recovered it to enable Denver to keep possession.
```

## Case 2

- Question ID: `56d71d150d65d2140019836f`
- Question: How many will the host committee dedicate to local charities?
- Saved final passages: 8
- Chunk identifiers stored: yes
- First-retrieval passage text: not stored. No row below uses it.

### Claim 1

```text
The Super Bowl 50 Host Committee has vowed to be 'the most giving Super Bowl ever', and will dedicate 25 percent of all money it raises for philanthropic causes in the Bay Area.
```

Stored aggregate result from `squad_cond_C.jsonl` `claim_results`:

- Verdict `INSUFFICIENT_EVIDENCE`; entailment 0.223246; contradiction 0.015425; uncertain `False`.
- Neutral probability: not stored. Per-premise probabilities: not stored. The premise that supplied each maximum: not stored.

Recomputed aggregate on these saved final passages, using `ClaimVerifier._premises` in joint mode and `ClaimVerifier._verdict` at 0.50. This recomputation is part of this diagnostic. It is not a new experiment result.

- Verdict `INSUFFICIENT_EVIDENCE`; entailment 0.223246; contradiction 0.015425; confidence 0.776754.
- Maximum entailment is premise index 1 (Passage 1).
- Maximum contradiction is premise index 1 (Passage 1).
- Those two maxima come from different premises: no.
- Recomputed aggregate matches the stored verdict and both scores within 1e-6: yes.

Pair-level rows use one saved final passage as the premise and this claim as the hypothesis. The verdict column applies the same 0.50 rule to that pair alone. It is not the verdict stored by Condition C.

| Passage | Chunk ID | Entailment | Contradiction | Neutral | Pair verdict | Differs from stored aggregate? | Role in recomputed aggregate |
|---|---|---:|---:|---:|---|---|---|
| P1 | `super_bowl_50-3302e76c::c0` | 0.223246 | 0.015425 | 0.761329 | `INSUFFICIENT_EVIDENCE` | No | max entailment in the joint premise list; max contradiction in the joint premise list |
| P2 | `super_bowl_50-c2f707a5::c0` | 0.000096 | 0.001092 | 0.998812 | `INSUFFICIENT_EVIDENCE` | No |  |
| P3 | `united_methodist_church-70d02d45::c0` | 0.000374 | 0.000419 | 0.999208 | `INSUFFICIENT_EVIDENCE` | No |  |
| P4 | `scottish_parliament-a868e82c::c0` | 0.000287 | 0.001374 | 0.998340 | `INSUFFICIENT_EVIDENCE` | No |  |
| P5 | `scottish_parliament-b44a57f7::c0` | 0.000815 | 0.003587 | 0.995598 | `INSUFFICIENT_EVIDENCE` | No |  |
| P6 | `super_bowl_50-521f1c84::c0` | 0.000100 | 0.001988 | 0.997912 | `INSUFFICIENT_EVIDENCE` | No |  |
| P7 | `super_bowl_50-d6975221::c0` | 0.000097 | 0.004141 | 0.995763 | `INSUFFICIENT_EVIDENCE` | No |  |
| P8 | `super_bowl_50-7d0d0b85::c0` | 0.000168 | 0.001777 | 0.998056 | `INSUFFICIENT_EVIDENCE` | No |  |

Verifier-constructed joint premise, not a retrieved passage: first 320 words of the saved final passages joined in order, capped at 320 words. Pair verdict on this constructed premise alone: `INSUFFICIENT_EVIDENCE` (entailment 0.005198, contradiction 0.000660, neutral 0.994142). This pair verdict differs from the stored aggregate: no.

```text
Super_Bowl_50: The Super Bowl 50 Host Committee has vowed to be "the most giving Super Bowl ever", and will dedicate 25 percent of all money it raises for philanthropic causes in the Bay Area. The committee created the 50 fund as its philanthropic initiative and focuses on providing grants to aid with youth development, community investment and sustainable environments. Super_Bowl_50: For the first time, the Super Bowl 50 Host Committee and the NFL have openly sought disabled veteran and lesbian, gay, bisexual and transgender-owned businesses in Business Connect, the Super Bowl program that provides local companies with contracting opportunities in and around the Super Bowl. The host committee has already raised over $40 million through sponsors including Apple, Google, Yahoo!, Intel, Gap, Chevron, and Dignity Health. United_Methodist_Church: Nevertheless, The United Methodist Church "implore[s] families and churches not to reject or condemn lesbian and gay members and friends" and commits itself to be in ministry with all persons, affirming that God's grace, love, and forgiveness is available to all. Additionally, many organizations, conferences, and congregations have recently called for broader acceptance of the LGBT community within the UMC. For example, the Connectional Table, a governing committee, has voted in favor of a proposal that calls for a localized option, which would permit ministers to officiate same-sex weddings, and it would allow conferences to ordain gay clergy. Moreover, many conferences have taken a position by voting in favor of same-gender marriages with resolutions. Scottish_Parliament: The first item of business on Wednesdays is usually Time for Reflection, at which a speaker addresses members for up to four minutes, sharing a perspective on issues of faith. This contrasts with the formal style of "Prayers", which is the first item of business in meetings of the House of Commons. Speakers are drawn from across Scotland and are chosen to represent the balance of religious beliefs according to the Scottish census. Invitations to address Parliament in
```

### Exact saved final passages

These strings are the Condition C `contexts` field. Passage numbers match the table above.

#### Passage 1

- Chunk ID: `super_bowl_50-3302e76c::c0`

```text
Super_Bowl_50: The Super Bowl 50 Host Committee has vowed to be "the most giving Super Bowl ever", and will dedicate 25 percent of all money it raises for philanthropic causes in the Bay Area. The committee created the 50 fund as its philanthropic initiative and focuses on providing grants to aid with youth development, community investment and sustainable environments.
```

#### Passage 2

- Chunk ID: `super_bowl_50-c2f707a5::c0`

```text
Super_Bowl_50: For the first time, the Super Bowl 50 Host Committee and the NFL have openly sought disabled veteran and lesbian, gay, bisexual and transgender-owned businesses in Business Connect, the Super Bowl program that provides local companies with contracting opportunities in and around the Super Bowl. The host committee has already raised over $40 million through sponsors including Apple, Google, Yahoo!, Intel, Gap, Chevron, and Dignity Health.
```

#### Passage 3

- Chunk ID: `united_methodist_church-70d02d45::c0`

```text
United_Methodist_Church: Nevertheless, The United Methodist Church "implore[s] families and churches not to reject or condemn lesbian and gay members and friends" and commits itself to be in ministry with all persons, affirming that God's grace, love, and forgiveness is available to all. Additionally, many organizations, conferences, and congregations have recently called for broader acceptance of the LGBT community within the UMC. For example, the Connectional Table, a governing committee, has voted in favor of a proposal that calls for a localized option, which would permit ministers to officiate same-sex weddings, and it would allow conferences to ordain gay clergy. Moreover, many conferences have taken a position by voting in favor of same-gender marriages with resolutions.
```

#### Passage 4

- Chunk ID: `scottish_parliament-a868e82c::c0`

```text
Scottish_Parliament: The first item of business on Wednesdays is usually Time for Reflection, at which a speaker addresses members for up to four minutes, sharing a perspective on issues of faith. This contrasts with the formal style of "Prayers", which is the first item of business in meetings of the House of Commons. Speakers are drawn from across Scotland and are chosen to represent the balance of religious beliefs according to the Scottish census. Invitations to address Parliament in this manner are determined by the Presiding Officer on the advice of the parliamentary bureau. Faith groups can make direct representations to the Presiding Officer to nominate speakers.
```

#### Passage 5

- Chunk ID: `scottish_parliament-b44a57f7::c0`

```text
Scottish_Parliament: Immediately after Decision Time a "Members Debate" is held, which lasts for 45 minutes. Members Business is a debate on a motion proposed by an MSP who is not a Scottish minister. Such motions are on issues which may be of interest to a particular area such as a member's own constituency, an upcoming or past event or any other item which would otherwise not be accorded official parliamentary time. As well as the proposer, other members normally contribute to the debate. The relevant minister, whose department the debate and motion relate to "winds up" the debate by speaking after all other participants.
```

#### Passage 6

- Chunk ID: `super_bowl_50-521f1c84::c0`

```text
Super_Bowl_50: In addition to the Vince Lombardi Trophy that all Super Bowl champions receive, the winner of Super Bowl 50 will also receive a large, 18-karat gold-plated "50". Each digit will weigh 33 lb (15 kg) for a total of 66 lb (30 kg). Like the Lombardi Trophy, the "50" will be designed by Tiffany & Co.
```

#### Passage 7

- Chunk ID: `super_bowl_50-d6975221::c0`

```text
Super_Bowl_50: The league announced on October 16, 2012, that the two finalists were Sun Life Stadium and Levi's Stadium. The South Florida/Miami area has previously hosted the event 10 times (tied for most with New Orleans), with the most recent one being Super Bowl XLIV in 2010. The San Francisco Bay Area last hosted in 1985 (Super Bowl XIX), held at Stanford Stadium in Stanford, California, won by the home team 49ers. The Miami bid depended on whether the stadium underwent renovations. However, on May 3, 2013, the Florida legislature refused to approve the funding plan to pay for the renovations, dealing a significant blow to Miami's chances.
```

#### Passage 8

- Chunk ID: `super_bowl_50-7d0d0b85::c0`

```text
Super_Bowl_50: On May 21, 2013, NFL owners at their spring meetings in Boston voted and awarded the game to Levi's Stadium. The $1.2 billion stadium opened in 2014. It is the first Super Bowl held in the San Francisco Bay Area since Super Bowl XIX in 1985, and the first in California since Super Bowl XXXVII took place in San Diego in 2003.
```

## Case 3

- Question ID: `56bf717d3aeaaa14008c9639`
- Question: Which video gaming company debuted their ad for the first time during Super Bowl 50?
- Saved final passages: 8
- Chunk identifiers stored: yes
- First-retrieval passage text: not stored. No row below uses it.

### Claim 1

```text
Nintendo and The Pokémon Company also made their Super Bowl debut, promoting the 20th anniversary of the Pokémon video game and media franchise.
```

Stored aggregate result from `squad_cond_C.jsonl` `claim_results`:

- Verdict `INSUFFICIENT_EVIDENCE`; entailment 0.000397; contradiction 0.017122; uncertain `False`.
- Neutral probability: not stored. Per-premise probabilities: not stored. The premise that supplied each maximum: not stored.

Recomputed aggregate on these saved final passages, using `ClaimVerifier._premises` in joint mode and `ClaimVerifier._verdict` at 0.50. This recomputation is part of this diagnostic. It is not a new experiment result.

- Verdict `INSUFFICIENT_EVIDENCE`; entailment 0.000397; contradiction 0.017122; confidence 0.982878.
- Maximum entailment is premise index 1 (Passage 1).
- Maximum contradiction is premise index 2 (Passage 2).
- Those two maxima come from different premises: yes.
- Recomputed aggregate matches the stored verdict and both scores within 1e-6: yes.

Pair-level rows use one saved final passage as the premise and this claim as the hypothesis. The verdict column applies the same 0.50 rule to that pair alone. It is not the verdict stored by Condition C.

| Passage | Chunk ID | Entailment | Contradiction | Neutral | Pair verdict | Differs from stored aggregate? | Role in recomputed aggregate |
|---|---|---:|---:|---:|---|---|---|
| P1 | `super_bowl_50-6e5e909f::c0` | 0.000397 | 0.009626 | 0.989977 | `INSUFFICIENT_EVIDENCE` | No | max entailment in the joint premise list |
| P2 | `super_bowl_50-6b0af9df::c0` | 0.000155 | 0.017122 | 0.982723 | `INSUFFICIENT_EVIDENCE` | No | max contradiction in the joint premise list |
| P3 | `super_bowl_50-c2f707a5::c0` | 0.000154 | 0.001767 | 0.998079 | `INSUFFICIENT_EVIDENCE` | No |  |
| P4 | `super_bowl_50-948ae07b::c0` | 0.000119 | 0.012641 | 0.987240 | `INSUFFICIENT_EVIDENCE` | No |  |
| P5 | `super_bowl_50-3785b3e2::c0` | 0.000217 | 0.008753 | 0.991030 | `INSUFFICIENT_EVIDENCE` | No |  |
| P6 | `super_bowl_50-7d0d0b85::c0` | 0.000292 | 0.004641 | 0.995067 | `INSUFFICIENT_EVIDENCE` | No |  |
| P7 | `super_bowl_50-3302e76c::c0` | 0.000257 | 0.001658 | 0.998084 | `INSUFFICIENT_EVIDENCE` | No |  |
| P8 | `super_bowl_50-49dbe46e::c0` | 0.000168 | 0.003412 | 0.996420 | `INSUFFICIENT_EVIDENCE` | No |  |

Verifier-constructed joint premise, not a retrieved passage: first 320 words of the saved final passages joined in order, capped at 320 words. Pair verdict on this constructed premise alone: `INSUFFICIENT_EVIDENCE` (entailment 0.000249, contradiction 0.004451, neutral 0.995300). This pair verdict differs from the stored aggregate: no.

```text
Super_Bowl_50: CBS set the base rate for a 30-second advertisement at $5,000,000, a record high price for a Super Bowl ad. As of January 26, the advertisements had not yet sold out. CBS mandated that all advertisers purchase a package covering time on both the television and digital broadcasts of the game, meaning that for the first time, digital streams of the game would carry all national advertising in pattern with the television broadcast. This would be the final year in a multi-year contract with Anheuser-Busch InBev that allowed the beer manufacturer to air multiple advertisements during the game at a steep discount. It was also the final year that Doritos, a longtime sponsor of the game, held its "Crash the Super Bowl" contest that allowed viewers to create their own Doritos ads for a chance to have it aired during the game. Nintendo and The Pokémon Company also made their Super Bowl debut, promoting the 20th anniversary of the Pokémon video game and media franchise. Super_Bowl_50: Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24–10 to earn their third Super Bowl title. The game was played on February 7, 2016, at Levi's Stadium in the San Francisco Bay Area at Santa Clara, California. As this was the 50th Super Bowl, the league emphasized the "golden anniversary" with various gold-themed initiatives, as well as temporarily suspending the tradition of naming each Super Bowl game with Roman numerals (under which the game would have been known as "Super Bowl L"), so that the logo could prominently feature the Arabic numerals 50. Super_Bowl_50: For the first time, the Super Bowl 50 Host Committee and the NFL have openly sought disabled veteran and lesbian, gay, bisexual and transgender-owned businesses in Business Connect,
```

### Exact saved final passages

These strings are the Condition C `contexts` field. Passage numbers match the table above.

#### Passage 1

- Chunk ID: `super_bowl_50-6e5e909f::c0`

```text
Super_Bowl_50: CBS set the base rate for a 30-second advertisement at $5,000,000, a record high price for a Super Bowl ad. As of January 26, the advertisements had not yet sold out. CBS mandated that all advertisers purchase a package covering time on both the television and digital broadcasts of the game, meaning that for the first time, digital streams of the game would carry all national advertising in pattern with the television broadcast. This would be the final year in a multi-year contract with Anheuser-Busch InBev that allowed the beer manufacturer to air multiple advertisements during the game at a steep discount. It was also the final year that Doritos, a longtime sponsor of the game, held its "Crash the Super Bowl" contest that allowed viewers to create their own Doritos ads for a chance to have it aired during the game. Nintendo and The Pokémon Company also made their Super Bowl debut, promoting the 20th anniversary of the Pokémon video game and media franchise.
```

#### Passage 2

- Chunk ID: `super_bowl_50-6b0af9df::c0`

```text
Super_Bowl_50: Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24–10 to earn their third Super Bowl title. The game was played on February 7, 2016, at Levi's Stadium in the San Francisco Bay Area at Santa Clara, California. As this was the 50th Super Bowl, the league emphasized the "golden anniversary" with various gold-themed initiatives, as well as temporarily suspending the tradition of naming each Super Bowl game with Roman numerals (under which the game would have been known as "Super Bowl L"), so that the logo could prominently feature the Arabic numerals 50.
```

#### Passage 3

- Chunk ID: `super_bowl_50-c2f707a5::c0`

```text
Super_Bowl_50: For the first time, the Super Bowl 50 Host Committee and the NFL have openly sought disabled veteran and lesbian, gay, bisexual and transgender-owned businesses in Business Connect, the Super Bowl program that provides local companies with contracting opportunities in and around the Super Bowl. The host committee has already raised over $40 million through sponsors including Apple, Google, Yahoo!, Intel, Gap, Chevron, and Dignity Health.
```

#### Passage 4

- Chunk ID: `super_bowl_50-948ae07b::c0`

```text
Super_Bowl_50: In early 2012, NFL Commissioner Roger Goodell stated that the league planned to make the 50th Super Bowl "spectacular" and that it would be "an important game for us as a league".
```

#### Passage 5

- Chunk ID: `super_bowl_50-3785b3e2::c0`

```text
Super_Bowl_50: Various gold-themed promotions and initiatives were held throughout the 2015 NFL season to tie into the "Golden Super Bowl"; gold-tinted logos were implemented across the NFL's properties and painted on fields, the numbering of the 50-yard line on fields was colored gold, and beginning on week 7, all sideline jackets and hats featured gold-trimmed logos. Gold footballs were given to each high school that has had a player or coach appear in the Super Bowl, and "homecoming" events were also held by Super Bowl-winning teams at games.
```

#### Passage 6

- Chunk ID: `super_bowl_50-7d0d0b85::c0`

```text
Super_Bowl_50: On May 21, 2013, NFL owners at their spring meetings in Boston voted and awarded the game to Levi's Stadium. The $1.2 billion stadium opened in 2014. It is the first Super Bowl held in the San Francisco Bay Area since Super Bowl XIX in 1985, and the first in California since Super Bowl XXXVII took place in San Diego in 2003.
```

#### Passage 7

- Chunk ID: `super_bowl_50-3302e76c::c0`

```text
Super_Bowl_50: The Super Bowl 50 Host Committee has vowed to be "the most giving Super Bowl ever", and will dedicate 25 percent of all money it raises for philanthropic causes in the Bay Area. The committee created the 50 fund as its philanthropic initiative and focuses on providing grants to aid with youth development, community investment and sustainable environments.
```

#### Passage 8

- Chunk ID: `super_bowl_50-49dbe46e::c0`

```text
Super_Bowl_50: On June 4, 2014, the NFL announced that the practice of branding Super Bowl games with Roman numerals, a practice established at Super Bowl V, would be temporarily suspended, and that the game would be named using Arabic numerals as Super Bowl 50 as opposed to Super Bowl L. The use of Roman numerals will be reinstated for Super Bowl LI. Jaime Weston, the league's vice president of brand and creative, explained that a primary reason for the change was the difficulty of designing an aesthetically pleasing logo with the letter "L" using the standardized logo template introduced at Super Bowl XLV. The logo also deviates from the template by featuring large numerals, colored in gold, behind the Vince Lombardi Trophy, instead of underneath and in silver as in the standard logo.
```

## Case 4

- Question ID: `56de1728cffd8e1900b4b5d7`
- Question: What was the Anglo-Norman language's final form?
- Saved final passages: 8
- Chunk identifiers stored: yes
- First-retrieval passage text: not stored. No row below uses it.

### Claim 1

```text
The Anglo-Norman language was eventually absorbed into the Anglo-Saxon language of their subjects (see Old English) and influenced it, helping (along with the Norse language of the earlier Anglo-Norse settlers and the Latin used by the church) in the development of Middle English.
```

Stored aggregate result from `squad_cond_C.jsonl` `claim_results`:

- Verdict `CONTRADICTED`; entailment 0.005994; contradiction 0.961947; uncertain `False`.
- Neutral probability: not stored. Per-premise probabilities: not stored. The premise that supplied each maximum: not stored.

Recomputed aggregate on these saved final passages, using `ClaimVerifier._premises` in joint mode and `ClaimVerifier._verdict` at 0.50. This recomputation is part of this diagnostic. It is not a new experiment result.

- Verdict `CONTRADICTED`; entailment 0.005994; contradiction 0.961947; confidence 0.961947.
- Maximum entailment is premise index 1 (Passage 1).
- Maximum contradiction is premise index 1 (Passage 1).
- Those two maxima come from different premises: no.
- Recomputed aggregate matches the stored verdict and both scores within 1e-6: yes.

Pair-level rows use one saved final passage as the premise and this claim as the hypothesis. The verdict column applies the same 0.50 rule to that pair alone. It is not the verdict stored by Condition C.

| Passage | Chunk ID | Entailment | Contradiction | Neutral | Pair verdict | Differs from stored aggregate? | Role in recomputed aggregate |
|---|---|---:|---:|---:|---|---|---|
| P1 | `normans-0b1edd8d::c0` | 0.005994 | 0.961947 | 0.032059 | `CONTRADICTED` | No | max entailment in the joint premise list; max contradiction in the joint premise list |
| P2 | `normans-9aa48ac3::c0` | 0.000377 | 0.007180 | 0.992443 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P3 | `normans-9b8d823d::c0` | 0.000438 | 0.002740 | 0.996822 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P4 | `huguenot-ec000e8d::c1` | 0.001898 | 0.007881 | 0.990222 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P5 | `normans-f9f1ea37::c0` | 0.001044 | 0.001220 | 0.997735 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P6 | `normans-d963cb53::c0` | 0.000621 | 0.069040 | 0.930339 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P7 | `huguenot-ad231892::c0` | 0.001631 | 0.004535 | 0.993834 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P8 | `french_and_indian_war-0c296b0d::c0` | 0.002056 | 0.139653 | 0.858290 | `INSUFFICIENT_EVIDENCE` | Yes |  |

Verifier-constructed joint premise, not a retrieved passage: first 320 words of the saved final passages joined in order, capped at 320 words. Pair verdict on this constructed premise alone: `INSUFFICIENT_EVIDENCE` (entailment 0.002835, contradiction 0.246938, neutral 0.750227). This pair verdict differs from the stored aggregate: yes.

```text
Normans: Eventually, the Normans merged with the natives, combining languages and traditions. In the course of the Hundred Years' War, the Norman aristocracy often identified themselves as English. The Anglo-Norman language became distinct from the Latin language, something that was the subject of some humour by Geoffrey Chaucer. The Anglo-Norman language was eventually absorbed into the Anglo-Saxon language of their subjects (see Old English) and influenced it, helping (along with the Norse language of the earlier Anglo-Norse settlers and the Latin used by the church) in the development of Middle English. It in turn evolved into Modern English. Normans: Normandy was the site of several important developments in the history of classical music in the 11th century. Fécamp Abbey and Saint-Evroul Abbey were centres of musical production and education. At Fécamp, under two Italian abbots, William of Volpiano and John of Ravenna, the system of denoting notes by letters was developed and taught. It is still the most common form of pitch representation in English- and German-speaking countries today. Also at Fécamp, the staff, around which neumes were oriented, was first developed and taught in the 11th century. Under the German abbot Isembard, La Trinité-du-Mont became a centre of musical composition. Normans: The Normans were in contact with England from an early date. Not only were their original Viking brethren still ravaging the English coasts, they occupied most of the important ports opposite England across the English Channel. This relationship eventually produced closer ties of blood through the marriage of Emma, sister of Duke Richard II of Normandy, and King Ethelred II of England. Because of this, Ethelred fled to Normandy in 1013, when he was forced from his kingdom by Sweyn Forkbeard. His stay in Normandy (until 1016) influenced him and his sons by Emma, who stayed in Normandy after Cnut the Great's conquest of the isle. Huguenot: Thus, Hugues plus Eidgenosse by way of Huisgenoten supposedly became Huguenot,
```

### Claim 2

```text
It in turn evolved into Modern English.
```

Stored aggregate result from `squad_cond_C.jsonl` `claim_results`:

- Verdict `INSUFFICIENT_EVIDENCE`; entailment 0.033238; contradiction 0.077837; uncertain `False`.
- Neutral probability: not stored. Per-premise probabilities: not stored. The premise that supplied each maximum: not stored.

Recomputed aggregate on these saved final passages, using `ClaimVerifier._premises` in joint mode and `ClaimVerifier._verdict` at 0.50. This recomputation is part of this diagnostic. It is not a new experiment result.

- Verdict `INSUFFICIENT_EVIDENCE`; entailment 0.033238; contradiction 0.077837; confidence 0.922163.
- Maximum entailment is premise index 1 (Passage 1).
- Maximum contradiction is premise index 0 (joint premise attributed to passages 1, 2, 3, 4, 5).
- Those two maxima come from different premises: yes.
- Recomputed aggregate matches the stored verdict and both scores within 1e-6: yes.

Pair-level rows use one saved final passage as the premise and this claim as the hypothesis. The verdict column applies the same 0.50 rule to that pair alone. It is not the verdict stored by Condition C.

| Passage | Chunk ID | Entailment | Contradiction | Neutral | Pair verdict | Differs from stored aggregate? | Role in recomputed aggregate |
|---|---|---:|---:|---:|---|---|---|
| P1 | `normans-0b1edd8d::c0` | 0.033238 | 0.065688 | 0.901074 | `INSUFFICIENT_EVIDENCE` | No | max entailment in the joint premise list |
| P2 | `normans-9aa48ac3::c0` | 0.000197 | 0.014763 | 0.985040 | `INSUFFICIENT_EVIDENCE` | No |  |
| P3 | `normans-9b8d823d::c0` | 0.000277 | 0.001213 | 0.998510 | `INSUFFICIENT_EVIDENCE` | No |  |
| P4 | `huguenot-ec000e8d::c1` | 0.000123 | 0.009523 | 0.990354 | `INSUFFICIENT_EVIDENCE` | No |  |
| P5 | `normans-f9f1ea37::c0` | 0.000634 | 0.001559 | 0.997807 | `INSUFFICIENT_EVIDENCE` | No |  |
| P6 | `normans-d963cb53::c0` | 0.000112 | 0.004705 | 0.995183 | `INSUFFICIENT_EVIDENCE` | No |  |
| P7 | `huguenot-ad231892::c0` | 0.000546 | 0.002122 | 0.997332 | `INSUFFICIENT_EVIDENCE` | No |  |
| P8 | `french_and_indian_war-0c296b0d::c0` | 0.000745 | 0.003153 | 0.996102 | `INSUFFICIENT_EVIDENCE` | No |  |

Verifier-constructed joint premise, not a retrieved passage: first 320 words of the saved final passages joined in order, capped at 320 words. Pair verdict on this constructed premise alone: `INSUFFICIENT_EVIDENCE` (entailment 0.002203, contradiction 0.077837, neutral 0.919960). This pair verdict differs from the stored aggregate: no.

```text
Normans: Eventually, the Normans merged with the natives, combining languages and traditions. In the course of the Hundred Years' War, the Norman aristocracy often identified themselves as English. The Anglo-Norman language became distinct from the Latin language, something that was the subject of some humour by Geoffrey Chaucer. The Anglo-Norman language was eventually absorbed into the Anglo-Saxon language of their subjects (see Old English) and influenced it, helping (along with the Norse language of the earlier Anglo-Norse settlers and the Latin used by the church) in the development of Middle English. It in turn evolved into Modern English. Normans: Normandy was the site of several important developments in the history of classical music in the 11th century. Fécamp Abbey and Saint-Evroul Abbey were centres of musical production and education. At Fécamp, under two Italian abbots, William of Volpiano and John of Ravenna, the system of denoting notes by letters was developed and taught. It is still the most common form of pitch representation in English- and German-speaking countries today. Also at Fécamp, the staff, around which neumes were oriented, was first developed and taught in the 11th century. Under the German abbot Isembard, La Trinité-du-Mont became a centre of musical composition. Normans: The Normans were in contact with England from an early date. Not only were their original Viking brethren still ravaging the English coasts, they occupied most of the important ports opposite England across the English Channel. This relationship eventually produced closer ties of blood through the marriage of Emma, sister of Duke Richard II of Normandy, and King Ethelred II of England. Because of this, Ethelred fled to Normandy in 1013, when he was forced from his kingdom by Sweyn Forkbeard. His stay in Normandy (until 1016) influenced him and his sons by Emma, who stayed in Normandy after Cnut the Great's conquest of the isle. Huguenot: Thus, Hugues plus Eidgenosse by way of Huisgenoten supposedly became Huguenot,
```

### Exact saved final passages

These strings are the Condition C `contexts` field. Passage numbers match the table above.

#### Passage 1

- Chunk ID: `normans-0b1edd8d::c0`

```text
Normans: Eventually, the Normans merged with the natives, combining languages and traditions. In the course of the Hundred Years' War, the Norman aristocracy often identified themselves as English. The Anglo-Norman language became distinct from the Latin language, something that was the subject of some humour by Geoffrey Chaucer. The Anglo-Norman language was eventually absorbed into the Anglo-Saxon language of their subjects (see Old English) and influenced it, helping (along with the Norse language of the earlier Anglo-Norse settlers and the Latin used by the church) in the development of Middle English. It in turn evolved into Modern English.
```

#### Passage 2

- Chunk ID: `normans-9aa48ac3::c0`

```text
Normans: Normandy was the site of several important developments in the history of classical music in the 11th century. Fécamp Abbey and Saint-Evroul Abbey were centres of musical production and education. At Fécamp, under two Italian abbots, William of Volpiano and John of Ravenna, the system of denoting notes by letters was developed and taught. It is still the most common form of pitch representation in English- and German-speaking countries today. Also at Fécamp, the staff, around which neumes were oriented, was first developed and taught in the 11th century. Under the German abbot Isembard, La Trinité-du-Mont became a centre of musical composition.
```

#### Passage 3

- Chunk ID: `normans-9b8d823d::c0`

```text
Normans: The Normans were in contact with England from an early date. Not only were their original Viking brethren still ravaging the English coasts, they occupied most of the important ports opposite England across the English Channel. This relationship eventually produced closer ties of blood through the marriage of Emma, sister of Duke Richard II of Normandy, and King Ethelred II of England. Because of this, Ethelred fled to Normandy in 1013, when he was forced from his kingdom by Sweyn Forkbeard. His stay in Normandy (until 1016) influenced him and his sons by Emma, who stayed in Normandy after Cnut the Great's conquest of the isle.
```

#### Passage 4

- Chunk ID: `huguenot-ec000e8d::c1`

```text
Huguenot: Thus, Hugues plus Eidgenosse by way of Huisgenoten supposedly became Huguenot, a nickname associating the Protestant cause with politics unpopular in France.[citation needed]
```

#### Passage 5

- Chunk ID: `normans-f9f1ea37::c0`

```text
Normans: Normans came into Scotland, building castles and founding noble families who would provide some future kings, such as Robert the Bruce, as well as founding a considerable number of the Scottish clans. King David I of Scotland, whose elder brother Alexander I had married Sybilla of Normandy, was instrumental in introducing Normans and Norman culture to Scotland, part of the process some scholars call the "Davidian Revolution". Having spent time at the court of Henry I of England (married to David's sister Maud of Scotland), and needing them to wrestle the kingdom from his half-brother Máel Coluim mac Alaxandair, David had to reward many with lands. The process was continued under David's successors, most intensely of all under William the Lion. The Norman-derived feudal system was applied in varying degrees to most of Scotland. Scottish families of the names Bruce, Gray, Ramsay, Fraser, Ogilvie, Montgomery, Sinclair, Pollock, Burnard, Douglas and Gordon to name but a few, and including the later royal House of Stewart, can all be traced back to Norman ancestry.
```

#### Passage 6

- Chunk ID: `normans-d963cb53::c0`

```text
Normans: The legendary religious zeal of the Normans was exercised in religious wars long before the First Crusade carved out a Norman principality in Antioch. They were major foreign participants in the Reconquista in Iberia. In 1018, Roger de Tosny travelled to the Iberian Peninsula to carve out a state for himself from Moorish lands, but failed. In 1064, during the War of Barbastro, William of Montreuil led the papal army and took a huge booty.
```

#### Passage 7

- Chunk ID: `huguenot-ad231892::c0`

```text
Huguenot: Most of the Huguenot congregations (or individuals) in North America eventually affiliated with other Protestant denominations with more numerous members. The Huguenots adapted quickly and often married outside their immediate French communities, which led to their assimilation. Their descendants in many families continued to use French first names and surnames for their children well into the nineteenth century. Assimilated, the French made numerous contributions to United States economic life, especially as merchants and artisans in the late Colonial and early Federal periods. For example, E.I. du Pont, a former student of Lavoisier, established the Eleutherian gunpowder mills.
```

#### Passage 8

- Chunk ID: `french_and_indian_war-0c296b0d::c0`

```text
French_and_Indian_War: The outcome was one of the most significant developments in a century of Anglo-French conflict. France ceded its territory east of the Mississippi to Great Britain. It ceded French Louisiana west of the Mississippi River (including New Orleans) to its ally Spain, in compensation for Spain's loss to Britain of Florida (Spain had ceded this to Britain in exchange for the return of Havana, Cuba). France's colonial presence north of the Caribbean was reduced to the islands of Saint Pierre and Miquelon, confirming Britain's position as the dominant colonial power in eastern North America.
```

## Case 5

- Question ID: `56bec5233aeaaa14008c93cf`
- Question: What radio station is located at 103.5FM on the dial in Denver?
- Saved final passages: 8
- Chunk identifiers stored: yes
- First-retrieval passage text: not stored. No row below uses it.

### Claim 1

```text
KRFX (103.5 FM) will carry the game in Denver, Colorado, during Super Bowl 50.
```

Stored aggregate result from `squad_cond_C.jsonl` `claim_results`:

- Verdict `CONTRADICTED`; entailment 0.483656; contradiction 0.983666; uncertain `True`.
- Neutral probability: not stored. Per-premise probabilities: not stored. The premise that supplied each maximum: not stored.

Recomputed aggregate on these saved final passages, using `ClaimVerifier._premises` in joint mode and `ClaimVerifier._verdict` at 0.50. This recomputation is part of this diagnostic. It is not a new experiment result.

- Verdict `CONTRADICTED`; entailment 0.483656; contradiction 0.983666; confidence 0.983666.
- Maximum entailment is premise index 1 (Passage 1).
- Maximum contradiction is premise index 6 (Passage 6).
- Those two maxima come from different premises: yes.
- Recomputed aggregate matches the stored verdict and both scores within 1e-6: yes.

Pair-level rows use one saved final passage as the premise and this claim as the hypothesis. The verdict column applies the same 0.50 rule to that pair alone. It is not the verdict stored by Condition C.

| Passage | Chunk ID | Entailment | Contradiction | Neutral | Pair verdict | Differs from stored aggregate? | Role in recomputed aggregate |
|---|---|---:|---:|---:|---|---|---|
| P1 | `super_bowl_50-e5544fa8::c0` | 0.483656 | 0.067038 | 0.449306 | `INSUFFICIENT_EVIDENCE` | Yes | max entailment in the joint premise list |
| P2 | `super_bowl_50-6b0af9df::c0` | 0.000485 | 0.002741 | 0.996774 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P3 | `packet_switching-1c748c9b::c0` | 0.000358 | 0.684032 | 0.315609 | `CONTRADICTED` | No |  |
| P4 | `american_broadcasting_company-5b310084::c1` | 0.000113 | 0.315222 | 0.684665 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P5 | `sky_united_kingdom-6dcbec62::c0` | 0.000085 | 0.007995 | 0.991920 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P6 | `super_bowl_50-9b7b8bf0::c0` | 0.000068 | 0.983666 | 0.016266 | `CONTRADICTED` | No | max contradiction in the joint premise list |
| P7 | `super_bowl_50-c1a5a40d::c0` | 0.000754 | 0.001147 | 0.998098 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P8 | `super_bowl_50-33632cb5::c0` | 0.000444 | 0.003515 | 0.996041 | `INSUFFICIENT_EVIDENCE` | Yes |  |

Verifier-constructed joint premise, not a retrieved passage: first 320 words of the saved final passages joined in order, capped at 320 words. Pair verdict on this constructed premise alone: `INSUFFICIENT_EVIDENCE` (entailment 0.001862, contradiction 0.002143, neutral 0.995995). This pair verdict differs from the stored aggregate: yes.

```text
Super_Bowl_50: The flagship stations of each station in the markets of each team will carry their local play-by-play calls. In Denver, KOA (850 AM) and KRFX (103.5 FM) will carry the game, with Dave Logan on play-by-play and Ed McCaffrey on color commentary. In North Carolina, WBT (1110 AM) will carry the game, with Mick Mixon on play-by-play and Eugene Robinson and Jim Szoke on color commentary. WBT will also simulcast the game on its sister station WBT-FM (99.3 FM), which is based in Chester, South Carolina. As KOA and WBT are both clear-channel stations, the local broadcasts will be audible over much of the western United States after sunset (for Denver) and the eastern United States throughout the game (for Carolina). In accordance with contractual rules, the rest of the stations in the Broncos and Panthers radio networks will either carry the Westwood One feed or not carry the game at all. Super_Bowl_50: Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24–10 to earn their third Super Bowl title. The game was played on February 7, 2016, at Levi's Stadium in the San Francisco Bay Area at Santa Clara, California. As this was the 50th Super Bowl, the league emphasized the "golden anniversary" with various gold-themed initiatives, as well as temporarily suspending the tradition of naming each Super Bowl game with Roman numerals (under which the game would have been known as "Super Bowl L"), so that the logo could prominently feature the Arabic numerals 50. Packet_switching: AppleTalk was a proprietary suite of networking protocols developed by Apple Inc. in 1985 for Apple Macintosh computers. It was the primary protocol used by Apple devices through the 1980s and 90s. AppleTalk included features that allowed local area networks to
```

### Exact saved final passages

These strings are the Condition C `contexts` field. Passage numbers match the table above.

#### Passage 1

- Chunk ID: `super_bowl_50-e5544fa8::c0`

```text
Super_Bowl_50: The flagship stations of each station in the markets of each team will carry their local play-by-play calls. In Denver, KOA (850 AM) and KRFX (103.5 FM) will carry the game, with Dave Logan on play-by-play and Ed McCaffrey on color commentary. In North Carolina, WBT (1110 AM) will carry the game, with Mick Mixon on play-by-play and Eugene Robinson and Jim Szoke on color commentary. WBT will also simulcast the game on its sister station WBT-FM (99.3 FM), which is based in Chester, South Carolina. As KOA and WBT are both clear-channel stations, the local broadcasts will be audible over much of the western United States after sunset (for Denver) and the eastern United States throughout the game (for Carolina). In accordance with contractual rules, the rest of the stations in the Broncos and Panthers radio networks will either carry the Westwood One feed or not carry the game at all.
```

#### Passage 2

- Chunk ID: `super_bowl_50-6b0af9df::c0`

```text
Super_Bowl_50: Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24–10 to earn their third Super Bowl title. The game was played on February 7, 2016, at Levi's Stadium in the San Francisco Bay Area at Santa Clara, California. As this was the 50th Super Bowl, the league emphasized the "golden anniversary" with various gold-themed initiatives, as well as temporarily suspending the tradition of naming each Super Bowl game with Roman numerals (under which the game would have been known as "Super Bowl L"), so that the logo could prominently feature the Arabic numerals 50.
```

#### Passage 3

- Chunk ID: `packet_switching-1c748c9b::c0`

```text
Packet_switching: AppleTalk was a proprietary suite of networking protocols developed by Apple Inc. in 1985 for Apple Macintosh computers. It was the primary protocol used by Apple devices through the 1980s and 90s. AppleTalk included features that allowed local area networks to be established ad hoc without the requirement for a centralized router or server. The AppleTalk system automatically assigned addresses, updated the distributed namespace, and configured any required inter-network routing. It was a plug-n-play system.
```

#### Passage 4

- Chunk ID: `american_broadcasting_company-5b310084::c1`

```text
American_Broadcasting_Company: Due to an FCC ban on same-market ownership of television and radio stations by a single company (although the deal would have otherwise complied with new ownership rules implemented by the FCC in January 1985, that allowed broadcasters to own a maximum of 12 television stations), ABC and Capital Cities respectively decided to sell WXYZ-TV and Tampa independent station WFTS-TV to the E. W. Scripps Company (although Capital Cities/ABC originally intended to seek a cross-ownership waiver to retain WXYZ and Capital Cities-owned radio stations WJR and WHYT).
```

#### Passage 5

- Chunk ID: `sky_united_kingdom-6dcbec62::c0`

```text
Sky_(United_Kingdom): BSkyB's direct-to-home satellite service became available in 10 million homes in 2010, Europe's first pay-TV platform in to achieve that milestone. Confirming it had reached its target, the broadcaster said its reach into 36% of households in the UK represented an audience of more than 25m people. The target was first announced in August 2004, since then an additional 2.4m customers had subscribed to BSkyB's direct-to-home service. Media commentators had debated whether the figure could be reached as the growth in subscriber numbers elsewhere in Europe flattened.
```

#### Passage 6

- Chunk ID: `super_bowl_50-9b7b8bf0::c0`

```text
Super_Bowl_50: Westwood One will carry the game throughout North America, with Kevin Harlan as play-by-play announcer, Boomer Esiason and Dan Fouts as color analysts, and James Lofton and Mark Malone as sideline reporters. Jim Gray will anchor the pre-game and halftime coverage.
```

#### Passage 7

- Chunk ID: `super_bowl_50-c1a5a40d::c0`

```text
Super_Bowl_50: The Broncos took an early lead in Super Bowl 50 and never trailed. Newton was limited by Denver's defense, which sacked him seven times and forced him into three turnovers, including a fumble which they recovered for a touchdown. Denver linebacker Von Miller was named Super Bowl MVP, recording five solo tackles, 21⁄2 sacks, and two forced fumbles.
```

#### Passage 8

- Chunk ID: `super_bowl_50-33632cb5::c0`

```text
Super_Bowl_50: As the designated home team in the annual rotation between AFC and NFC teams, the Broncos elected to wear their road white jerseys with matching white pants. Elway stated, "We've had Super Bowl success in our white uniforms." The Broncos last wore matching white jerseys and pants in the Super Bowl in Super Bowl XXXIII, Elway's last game as Denver QB, when they defeated the Atlanta Falcons 34–19. In their only other Super Bowl win in Super Bowl XXXII, Denver wore blue jerseys, which was their primary color at the time. They also lost Super Bowl XXI when they wore white jerseys, but they are 0-4 in Super Bowls when wearing orange jerseys, losing in Super Bowl XII, XXII, XXIV, and XLVIII. The only other AFC champion team to have worn white as the designated home team in the Super Bowl was the Pittsburgh Steelers; they defeated the Seattle Seahawks 21–10 in Super Bowl XL 10 seasons prior. The Broncos' decision to wear white meant the Panthers would wear their standard home uniform: black jerseys with silver pants.
```

## Case 6

- Question ID: `56bf48cc3aeaaa14008c95ab`
- Question: What was the last game that Elway played as a quarterback for Denver?
- Saved final passages: 8
- Chunk identifiers stored: yes
- First-retrieval passage text: not stored. No row below uses it.

### Claim 1

```text
Elway's last game as Denver QB was Super Bowl XXXII.
```

Stored aggregate result from `squad_cond_C.jsonl` `claim_results`:

- Verdict `CONTRADICTED`; entailment 0.007959; contradiction 0.988750; uncertain `False`.
- Neutral probability: not stored. Per-premise probabilities: not stored. The premise that supplied each maximum: not stored.

Recomputed aggregate on these saved final passages, using `ClaimVerifier._premises` in joint mode and `ClaimVerifier._verdict` at 0.50. This recomputation is part of this diagnostic. It is not a new experiment result.

- Verdict `CONTRADICTED`; entailment 0.007959; contradiction 0.988750; confidence 0.988750.
- Maximum entailment is premise index 1 (Passage 1).
- Maximum contradiction is premise index 3 (Passage 3).
- Those two maxima come from different premises: yes.
- Recomputed aggregate matches the stored verdict and both scores within 1e-6: yes.

Pair-level rows use one saved final passage as the premise and this claim as the hypothesis. The verdict column applies the same 0.50 rule to that pair alone. It is not the verdict stored by Condition C.

| Passage | Chunk ID | Entailment | Contradiction | Neutral | Pair verdict | Differs from stored aggregate? | Role in recomputed aggregate |
|---|---|---:|---:|---:|---|---|---|
| P1 | `super_bowl_50-33632cb5::c0` | 0.007959 | 0.096246 | 0.895796 | `INSUFFICIENT_EVIDENCE` | Yes | max entailment in the joint premise list |
| P2 | `super_bowl_50-6b0af9df::c0` | 0.000233 | 0.002311 | 0.997456 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P3 | `super_bowl_50-31d37d05::c0` | 0.000389 | 0.988750 | 0.010862 | `CONTRADICTED` | No | max contradiction in the joint premise list |
| P4 | `super_bowl_50-f1b96eb2::c0` | 0.001173 | 0.008693 | 0.990133 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P5 | `super_bowl_50-a533c800::c0` | 0.000972 | 0.070207 | 0.928821 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P6 | `super_bowl_50-49dbe46e::c0` | 0.000422 | 0.005704 | 0.993874 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P7 | `super_bowl_50-3785b3e2::c0` | 0.000167 | 0.904275 | 0.095558 | `CONTRADICTED` | No |  |
| P8 | `super_bowl_50-c1a5a40d::c0` | 0.000378 | 0.010030 | 0.989592 | `INSUFFICIENT_EVIDENCE` | Yes |  |

Verifier-constructed joint premise, not a retrieved passage: first 320 words of the saved final passages joined in order, capped at 320 words. Pair verdict on this constructed premise alone: `INSUFFICIENT_EVIDENCE` (entailment 0.000715, contradiction 0.004802, neutral 0.994483). This pair verdict differs from the stored aggregate: yes.

```text
Super_Bowl_50: As the designated home team in the annual rotation between AFC and NFC teams, the Broncos elected to wear their road white jerseys with matching white pants. Elway stated, "We've had Super Bowl success in our white uniforms." The Broncos last wore matching white jerseys and pants in the Super Bowl in Super Bowl XXXIII, Elway's last game as Denver QB, when they defeated the Atlanta Falcons 34–19. In their only other Super Bowl win in Super Bowl XXXII, Denver wore blue jerseys, which was their primary color at the time. They also lost Super Bowl XXI when they wore white jerseys, but they are 0-4 in Super Bowls when wearing orange jerseys, losing in Super Bowl XII, XXII, XXIV, and XLVIII. The only other AFC champion team to have worn white as the designated home team in the Super Bowl was the Pittsburgh Steelers; they defeated the Seattle Seahawks 21–10 in Super Bowl XL 10 seasons prior. The Broncos' decision to wear white meant the Panthers would wear their standard home uniform: black jerseys with silver pants. Super_Bowl_50: Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24–10 to earn their third Super Bowl title. The game was played on February 7, 2016, at Levi's Stadium in the San Francisco Bay Area at Santa Clara, California. As this was the 50th Super Bowl, the league emphasized the "golden anniversary" with various gold-themed initiatives, as well as temporarily suspending the tradition of naming each Super Bowl game with Roman numerals (under which the game would have been known as "Super Bowl L"), so that the logo could prominently feature the Arabic numerals 50. Super_Bowl_50: The Broncos defeated the Pittsburgh Steelers in the divisional round, 23–16, by scoring 11 points
```

### Exact saved final passages

These strings are the Condition C `contexts` field. Passage numbers match the table above.

#### Passage 1

- Chunk ID: `super_bowl_50-33632cb5::c0`

```text
Super_Bowl_50: As the designated home team in the annual rotation between AFC and NFC teams, the Broncos elected to wear their road white jerseys with matching white pants. Elway stated, "We've had Super Bowl success in our white uniforms." The Broncos last wore matching white jerseys and pants in the Super Bowl in Super Bowl XXXIII, Elway's last game as Denver QB, when they defeated the Atlanta Falcons 34–19. In their only other Super Bowl win in Super Bowl XXXII, Denver wore blue jerseys, which was their primary color at the time. They also lost Super Bowl XXI when they wore white jerseys, but they are 0-4 in Super Bowls when wearing orange jerseys, losing in Super Bowl XII, XXII, XXIV, and XLVIII. The only other AFC champion team to have worn white as the designated home team in the Super Bowl was the Pittsburgh Steelers; they defeated the Seattle Seahawks 21–10 in Super Bowl XL 10 seasons prior. The Broncos' decision to wear white meant the Panthers would wear their standard home uniform: black jerseys with silver pants.
```

#### Passage 2

- Chunk ID: `super_bowl_50-6b0af9df::c0`

```text
Super_Bowl_50: Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24–10 to earn their third Super Bowl title. The game was played on February 7, 2016, at Levi's Stadium in the San Francisco Bay Area at Santa Clara, California. As this was the 50th Super Bowl, the league emphasized the "golden anniversary" with various gold-themed initiatives, as well as temporarily suspending the tradition of naming each Super Bowl game with Roman numerals (under which the game would have been known as "Super Bowl L"), so that the logo could prominently feature the Arabic numerals 50.
```

#### Passage 3

- Chunk ID: `super_bowl_50-31d37d05::c0`

```text
Super_Bowl_50: The Broncos defeated the Pittsburgh Steelers in the divisional round, 23–16, by scoring 11 points in the final three minutes of the game. They then beat the defending Super Bowl XLIX champion New England Patriots in the AFC Championship Game, 20–18, by intercepting a pass on New England's 2-point conversion attempt with 17 seconds left on the clock. Despite Manning's problems with interceptions during the season, he didn't throw any in their two playoff games.
```

#### Passage 4

- Chunk ID: `super_bowl_50-f1b96eb2::c0`

```text
Super_Bowl_50: The Panthers finished the regular season with a 15–1 record, and quarterback Cam Newton was named the NFL Most Valuable Player (MVP). They defeated the Arizona Cardinals 49–15 in the NFC Championship Game and advanced to their second Super Bowl appearance since the franchise was founded in 1995. The Broncos finished the regular season with a 12–4 record, and denied the New England Patriots a chance to defend their title from Super Bowl XLIX by defeating them 20–18 in the AFC Championship Game. They joined the Patriots, Dallas Cowboys, and Pittsburgh Steelers as one of four teams that have made eight appearances in the Super Bowl.
```

#### Passage 5

- Chunk ID: `super_bowl_50-a533c800::c0`

```text
Super_Bowl_50: The Panthers seemed primed to score on their opening drive of the second half when Newton completed a 45-yard pass to Ted Ginn Jr. on the Denver 35-yard line on their second offensive play. But the Broncos defense halted the drive on the 26-yard line, and it ended with no points when Graham Gano hit the uprights on a 44-yard field goal attempt. After the miss, Manning completed a pair of passes to Emmanuel Sanders for gains of 25 and 22 yards, setting up McManus' 33-yard field goal that gave the Broncos a 16–7 lead. Carolina got off to another strong start after the kickoff, with Newton completing a 42-yard pass to Corey Brown. But once again they came up empty, this time as a result of a Newton pass that bounced off the hands of Ginn and was intercepted by safety T. J. Ward. Ward fumbled the ball during the return, but Trevathan recovered it to enable Denver to keep possession.
```

#### Passage 6

- Chunk ID: `super_bowl_50-49dbe46e::c0`

```text
Super_Bowl_50: On June 4, 2014, the NFL announced that the practice of branding Super Bowl games with Roman numerals, a practice established at Super Bowl V, would be temporarily suspended, and that the game would be named using Arabic numerals as Super Bowl 50 as opposed to Super Bowl L. The use of Roman numerals will be reinstated for Super Bowl LI. Jaime Weston, the league's vice president of brand and creative, explained that a primary reason for the change was the difficulty of designing an aesthetically pleasing logo with the letter "L" using the standardized logo template introduced at Super Bowl XLV. The logo also deviates from the template by featuring large numerals, colored in gold, behind the Vince Lombardi Trophy, instead of underneath and in silver as in the standard logo.
```

#### Passage 7

- Chunk ID: `super_bowl_50-3785b3e2::c0`

```text
Super_Bowl_50: Various gold-themed promotions and initiatives were held throughout the 2015 NFL season to tie into the "Golden Super Bowl"; gold-tinted logos were implemented across the NFL's properties and painted on fields, the numbering of the 50-yard line on fields was colored gold, and beginning on week 7, all sideline jackets and hats featured gold-trimmed logos. Gold footballs were given to each high school that has had a player or coach appear in the Super Bowl, and "homecoming" events were also held by Super Bowl-winning teams at games.
```

#### Passage 8

- Chunk ID: `super_bowl_50-c1a5a40d::c0`

```text
Super_Bowl_50: The Broncos took an early lead in Super Bowl 50 and never trailed. Newton was limited by Denver's defense, which sacked him seven times and forced him into three turnovers, including a fumble which they recovered for a touchdown. Denver linebacker Von Miller was named Super Bowl MVP, recording five solo tackles, 21⁄2 sacks, and two forced fumbles.
```

## Case 7

- Question ID: `57335c20d058e614000b58f9`
- Question: How many geomorphologic formations is Warsaw on?
- Saved final passages: 8
- Chunk identifiers stored: yes
- First-retrieval passage text: not stored. No row below uses it.

### Claim 1

```text
Warsaw is located on two main geomorphologic formations: the plain moraine plateau and the Vistula Valley with its asymmetrical pattern of different terraces.
```

Stored aggregate result from `squad_cond_C.jsonl` `claim_results`:

- Verdict `CONTRADICTED`; entailment 0.021358; contradiction 0.991725; uncertain `False`.
- Neutral probability: not stored. Per-premise probabilities: not stored. The premise that supplied each maximum: not stored.

Recomputed aggregate on these saved final passages, using `ClaimVerifier._premises` in joint mode and `ClaimVerifier._verdict` at 0.50. This recomputation is part of this diagnostic. It is not a new experiment result.

- Verdict `CONTRADICTED`; entailment 0.021358; contradiction 0.991725; confidence 0.991725.
- Maximum entailment is premise index 2 (Passage 2).
- Maximum contradiction is premise index 8 (Passage 8).
- Those two maxima come from different premises: yes.
- Recomputed aggregate matches the stored verdict and both scores within 1e-6: yes.

Pair-level rows use one saved final passage as the premise and this claim as the hypothesis. The verdict column applies the same 0.50 rule to that pair alone. It is not the verdict stored by Condition C.

| Passage | Chunk ID | Entailment | Contradiction | Neutral | Pair verdict | Differs from stored aggregate? | Role in recomputed aggregate |
|---|---|---:|---:|---:|---|---|---|
| P1 | `warsaw-2e435d34::c0` | 0.014310 | 0.004028 | 0.981662 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P2 | `warsaw-93027874::c0` | 0.021358 | 0.254802 | 0.723840 | `INSUFFICIENT_EVIDENCE` | Yes | max entailment in the joint premise list |
| P3 | `warsaw-251afb78::c0` | 0.003052 | 0.974586 | 0.022361 | `CONTRADICTED` | No |  |
| P4 | `warsaw-f79e622c::c0` | 0.001128 | 0.209922 | 0.788950 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P5 | `warsaw-236c166e::c0` | 0.002642 | 0.138049 | 0.859310 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P6 | `warsaw-f5877edb::c0` | 0.007572 | 0.492823 | 0.499605 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P7 | `warsaw-490d76fe::c0` | 0.003722 | 0.534296 | 0.461982 | `CONTRADICTED` | No |  |
| P8 | `warsaw-a2b521b6::c0` | 0.000055 | 0.991725 | 0.008221 | `CONTRADICTED` | No | max contradiction in the joint premise list |

Verifier-constructed joint premise, not a retrieved passage: first 320 words of the saved final passages joined in order, capped at 320 words. Pair verdict on this constructed premise alone: `INSUFFICIENT_EVIDENCE` (entailment 0.005763, contradiction 0.011114, neutral 0.983123). This pair verdict differs from the stored aggregate: yes.

```text
Warsaw: Warsaw is located on two main geomorphologic formations: the plain moraine plateau and the Vistula Valley with its asymmetrical pattern of different terraces. The Vistula River is the specific axis of Warsaw, which divides the city into two parts, left and right. The left one is situated both on the moraine plateau (10 to 25 m (32.8 to 82.0 ft) above Vistula level) and on the Vistula terraces (max. 6.5 m (21.3 ft) above Vistula level). The significant element of the relief, in this part of Warsaw, is the edge of moraine plateau called Warsaw Escarpment. It is 20 to 25 m (65.6 to 82.0 ft) high in the Old Town and Central district and about 10 m (32.8 ft) in the north and south of Warsaw. It goes through the city and plays an important role as a landmark. Warsaw: Warsaw lies in east-central Poland about 300 km (190 mi) from the Carpathian Mountains and about 260 km (160 mi) from the Baltic Sea, 523 km (325 mi) east of Berlin, Germany. The city straddles the Vistula River. It is located in the heartland of the Masovian Plain, and its average elevation is 100 metres (330 ft) above sea level. The highest point on the left side of the city lies at a height of 115.7 metres (379.6 ft) ("Redutowa" bus depot, district of Wola), on the right side – 122.1 metres (400.6 ft) ("Groszówka" estate, district of Wesoła, by the eastern border). The lowest point lies at a height 75.6 metres (248.0 ft) (at the right bank of the Vistula, by the eastern border of Warsaw). There are some hills (mostly artificial) located within the confines of the city – e.g. Warsaw Uprising Hill (121 metres (397.0 ft)), Szczęśliwice hill (138 metres (452.8 ft) – the highest point of Warsaw in general). Warsaw: Warsaw (Polish: Warszawa [varˈʂava] ( listen); see also other names) is the capital and
```

### Exact saved final passages

These strings are the Condition C `contexts` field. Passage numbers match the table above.

#### Passage 1

- Chunk ID: `warsaw-2e435d34::c0`

```text
Warsaw: Warsaw is located on two main geomorphologic formations: the plain moraine plateau and the Vistula Valley with its asymmetrical pattern of different terraces. The Vistula River is the specific axis of Warsaw, which divides the city into two parts, left and right. The left one is situated both on the moraine plateau (10 to 25 m (32.8 to 82.0 ft) above Vistula level) and on the Vistula terraces (max. 6.5 m (21.3 ft) above Vistula level). The significant element of the relief, in this part of Warsaw, is the edge of moraine plateau called Warsaw Escarpment. It is 20 to 25 m (65.6 to 82.0 ft) high in the Old Town and Central district and about 10 m (32.8 ft) in the north and south of Warsaw. It goes through the city and plays an important role as a landmark.
```

#### Passage 2

- Chunk ID: `warsaw-93027874::c0`

```text
Warsaw: Warsaw lies in east-central Poland about 300 km (190 mi) from the Carpathian Mountains and about 260 km (160 mi) from the Baltic Sea, 523 km (325 mi) east of Berlin, Germany. The city straddles the Vistula River. It is located in the heartland of the Masovian Plain, and its average elevation is 100 metres (330 ft) above sea level. The highest point on the left side of the city lies at a height of 115.7 metres (379.6 ft) ("Redutowa" bus depot, district of Wola), on the right side – 122.1 metres (400.6 ft) ("Groszówka" estate, district of Wesoła, by the eastern border). The lowest point lies at a height 75.6 metres (248.0 ft) (at the right bank of the Vistula, by the eastern border of Warsaw). There are some hills (mostly artificial) located within the confines of the city – e.g. Warsaw Uprising Hill (121 metres (397.0 ft)), Szczęśliwice hill (138 metres (452.8 ft) – the highest point of Warsaw in general).
```

#### Passage 3

- Chunk ID: `warsaw-251afb78::c0`

```text
Warsaw: Warsaw (Polish: Warszawa [varˈʂava] ( listen); see also other names) is the capital and largest city of Poland. It stands on the Vistula River in east-central Poland, roughly 260 kilometres (160 mi) from the Baltic Sea and 300 kilometres (190 mi) from the Carpathian Mountains. Its population is estimated at 1.740 million residents within a greater metropolitan area of 2.666 million residents, which makes Warsaw the 9th most-populous capital city in the European Union. The city limits cover 516.9 square kilometres (199.6 sq mi), while the metropolitan area covers 6,100.43 square kilometres (2,355.39 sq mi).
```

#### Passage 4

- Chunk ID: `warsaw-f79e622c::c0`

```text
Warsaw: There are 13 natural reserves in Warsaw – among others, Bielany Forest, Kabaty Woods, Czerniaków Lake. About 15 kilometres (9 miles) from Warsaw, the Vistula river's environment changes strikingly and features a perfectly preserved ecosystem, with a habitat of animals that includes the otter, beaver and hundreds of bird species. There are also several lakes in Warsaw – mainly the oxbow lakes, like Czerniaków Lake, the lakes in the Łazienki or Wilanów Parks, Kamionek Lake. There are lot of small lakes in the parks, but only a few are permanent – the majority are emptied before winter to clean them of plants and sediments.
```

#### Passage 5

- Chunk ID: `warsaw-236c166e::c0`

```text
Warsaw: After World War II, under a Communist regime set up by the conquering Soviets, the "Bricks for Warsaw" campaign was initiated, and large prefabricated housing projects were erected in Warsaw to address the housing shortage, along with other typical buildings of an Eastern Bloc city, such as the Palace of Culture and Science, a gift from the Soviet Union. The city resumed its role as the capital of Poland and the country's centre of political and economic life. Many of the historic streets, buildings, and churches were restored to their original form. In 1980, Warsaw's historic Old Town was inscribed onto UNESCO's World Heritage list.
```

#### Passage 6

- Chunk ID: `warsaw-f5877edb::c0`

```text
Warsaw: Warsaw was occupied by Germany from 4 August 1915 until November 1918. The Allied Armistice terms required in Article 12 that Germany withdraw from areas controlled by Russia in 1914, which included Warsaw. Germany did so, and underground leader Piłsudski returned to Warsaw on 11 November and set up what became the Second Polish Republic, with Warsaw the capital. In the course of the Polish-Bolshevik War of 1920, the huge Battle of Warsaw was fought on the eastern outskirts of the city in which the capital was successfully defended and the Red Army defeated. Poland stopped by itself the full brunt of the Red Army and defeated an idea of the "export of the revolution".
```

#### Passage 7

- Chunk ID: `warsaw-490d76fe::c0`

```text
Warsaw: Warsaw's name in the Polish language is Warszawa, approximately /vɑːrˈʃɑːvə/ (also formerly spelled Warszewa and Warszowa), meaning "belonging to Warsz", Warsz being a shortened form of the masculine name of Slavic origin Warcisław; see also etymology of Wrocław. Folk etymology attributes the city name to a fisherman, Wars, and his wife, Sawa. According to legend, Sawa was a mermaid living in the Vistula River with whom Wars fell in love. In actuality, Warsz was a 12th/13th-century nobleman who owned a village located at the modern-day site of Mariensztat neighbourhood. See also the Vršovci family which had escaped to Poland. The official city name in full is miasto stołeczne Warszawa (English: "The Capital City of Warsaw"). A native or resident of Warsaw is known as a Varsovian – in Polish warszawiak (male), warszawianka (female), warszawiacy (plural).
```

#### Passage 8

- Chunk ID: `warsaw-a2b521b6::c0`

```text
Warsaw: Warsaw remained the capital of the Polish–Lithuanian Commonwealth until 1796, when it was annexed by the Kingdom of Prussia to become the capital of the province of South Prussia. Liberated by Napoleon's army in 1806, Warsaw was made the capital of the newly created Duchy of Warsaw. Following the Congress of Vienna of 1815, Warsaw became the centre of the Congress Poland, a constitutional monarchy under a personal union with Imperial Russia. The Royal University of Warsaw was established in 1816.
```

## Case 8

- Question ID: `56d6f3500d65d21400198290`
- Question: How many interceptions are the Panthers defense credited with in 2015?
- Saved final passages: 8
- Chunk identifiers stored: yes
- First-retrieval passage text: not stored. No row below uses it.

### Claim 1

```text
The Panthers defense gave up just 308 points, ranking sixth in the league, while also leading the NFL in interceptions with 24 and boasting four Pro Bowl selections.
```

Stored aggregate result from `squad_cond_C.jsonl` `claim_results`:

- Verdict `CONTRADICTED`; entailment 0.013579; contradiction 0.996119; uncertain `False`.
- Neutral probability: not stored. Per-premise probabilities: not stored. The premise that supplied each maximum: not stored.

Recomputed aggregate on these saved final passages, using `ClaimVerifier._premises` in joint mode and `ClaimVerifier._verdict` at 0.50. This recomputation is part of this diagnostic. It is not a new experiment result.

- Verdict `CONTRADICTED`; entailment 0.013579; contradiction 0.996119; confidence 0.996119.
- Maximum entailment is premise index 0 (joint premise attributed to passages 1, 2, 3, 4, 5).
- Maximum contradiction is premise index 2 (Passage 2).
- Those two maxima come from different premises: yes.
- Recomputed aggregate matches the stored verdict and both scores within 1e-6: yes.

Pair-level rows use one saved final passage as the premise and this claim as the hypothesis. The verdict column applies the same 0.50 rule to that pair alone. It is not the verdict stored by Condition C.

| Passage | Chunk ID | Entailment | Contradiction | Neutral | Pair verdict | Differs from stored aggregate? | Role in recomputed aggregate |
|---|---|---:|---:|---:|---|---|---|
| P1 | `super_bowl_50-b90a9e1e::c0` | 0.001655 | 0.001329 | 0.997016 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P2 | `super_bowl_50-de8c4f45::c0` | 0.000129 | 0.996119 | 0.003752 | `CONTRADICTED` | No | max contradiction in the joint premise list |
| P3 | `super_bowl_50-f1b96eb2::c0` | 0.000731 | 0.023240 | 0.976029 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P4 | `super_bowl_50-c2358d5d::c0` | 0.000760 | 0.845835 | 0.153405 | `CONTRADICTED` | No |  |
| P5 | `super_bowl_50-aad58c5e::c0` | 0.000239 | 0.004021 | 0.995740 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P6 | `super_bowl_50-bcf54c0b::c0` | 0.000256 | 0.018494 | 0.981250 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P7 | `super_bowl_50-a533c800::c0` | 0.000333 | 0.058269 | 0.941398 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P8 | `super_bowl_50-31d37d05::c0` | 0.000231 | 0.989826 | 0.009943 | `CONTRADICTED` | No |  |

Verifier-constructed joint premise, not a retrieved passage: first 320 words of the saved final passages joined in order, capped at 320 words. Pair verdict on this constructed premise alone: `CONTRADICTED` (entailment 0.013579, contradiction 0.551033, neutral 0.435388). This pair verdict differs from the stored aggregate: no.

```text
Super_Bowl_50: The Panthers defense gave up just 308 points, ranking sixth in the league, while also leading the NFL in interceptions with 24 and boasting four Pro Bowl selections. Pro Bowl defensive tackle Kawann Short led the team in sacks with 11, while also forcing three fumbles and recovering two. Fellow lineman Mario Addison added 61⁄2 sacks. The Panthers line also featured veteran defensive end Jared Allen, a 5-time pro bowler who was the NFL's active career sack leader with 136, along with defensive end Kony Ealy, who had 5 sacks in just 9 starts. Behind them, two of the Panthers three starting linebackers were also selected to play in the Pro Bowl: Thomas Davis and Luke Kuechly. Davis compiled 51⁄2 sacks, four forced fumbles, and four interceptions, while Kuechly led the team in tackles (118) forced two fumbles, and intercepted four passes of his own. Carolina's secondary featured Pro Bowl safety Kurt Coleman, who led the team with a career high seven interceptions, while also racking up 88 tackles and Pro Bowl cornerback Josh Norman, who developed into a shutdown corner during the season and had four interceptions, two of which were returned for touchdowns. Super_Bowl_50: On Carolina's next possession fullback Mike Tolbert lost a fumble while being tackled by safety Darian Stewart, which linebacker Danny Trevathan recovered on the Broncos 40-yard line. However, the Panthers soon took the ball back when defensive end Kony Ealy tipped a Manning pass to himself and then intercepted it, returning the ball 19 yards to the Panthers 39-yard line with 1:55 left on the clock. The Panthers could not gain any yards with their possession and had to punt. After a Denver punt, Carolina drove to the Broncos 45-yard line. But with 11 seconds left, Newton was sacked by DeMarcus Ware as time expired in the half. Super_Bowl_50: The Panthers finished the regular season with a 15–1 record, and quarterback Cam Newton
```

### Exact saved final passages

These strings are the Condition C `contexts` field. Passage numbers match the table above.

#### Passage 1

- Chunk ID: `super_bowl_50-b90a9e1e::c0`

```text
Super_Bowl_50: The Panthers defense gave up just 308 points, ranking sixth in the league, while also leading the NFL in interceptions with 24 and boasting four Pro Bowl selections. Pro Bowl defensive tackle Kawann Short led the team in sacks with 11, while also forcing three fumbles and recovering two. Fellow lineman Mario Addison added 61⁄2 sacks. The Panthers line also featured veteran defensive end Jared Allen, a 5-time pro bowler who was the NFL's active career sack leader with 136, along with defensive end Kony Ealy, who had 5 sacks in just 9 starts. Behind them, two of the Panthers three starting linebackers were also selected to play in the Pro Bowl: Thomas Davis and Luke Kuechly. Davis compiled 51⁄2 sacks, four forced fumbles, and four interceptions, while Kuechly led the team in tackles (118) forced two fumbles, and intercepted four passes of his own. Carolina's secondary featured Pro Bowl safety Kurt Coleman, who led the team with a career high seven interceptions, while also racking up 88 tackles and Pro Bowl cornerback Josh Norman, who developed into a shutdown corner during the season and had four interceptions, two of which were returned for touchdowns.
```

#### Passage 2

- Chunk ID: `super_bowl_50-de8c4f45::c0`

```text
Super_Bowl_50: On Carolina's next possession fullback Mike Tolbert lost a fumble while being tackled by safety Darian Stewart, which linebacker Danny Trevathan recovered on the Broncos 40-yard line. However, the Panthers soon took the ball back when defensive end Kony Ealy tipped a Manning pass to himself and then intercepted it, returning the ball 19 yards to the Panthers 39-yard line with 1:55 left on the clock. The Panthers could not gain any yards with their possession and had to punt. After a Denver punt, Carolina drove to the Broncos 45-yard line. But with 11 seconds left, Newton was sacked by DeMarcus Ware as time expired in the half.
```

#### Passage 3

- Chunk ID: `super_bowl_50-f1b96eb2::c0`

```text
Super_Bowl_50: The Panthers finished the regular season with a 15–1 record, and quarterback Cam Newton was named the NFL Most Valuable Player (MVP). They defeated the Arizona Cardinals 49–15 in the NFC Championship Game and advanced to their second Super Bowl appearance since the franchise was founded in 1995. The Broncos finished the regular season with a 12–4 record, and denied the New England Patriots a chance to defend their title from Super Bowl XLIX by defeating them 20–18 in the AFC Championship Game. They joined the Patriots, Dallas Cowboys, and Pittsburgh Steelers as one of four teams that have made eight appearances in the Super Bowl.
```

#### Passage 4

- Chunk ID: `super_bowl_50-c2358d5d::c0`

```text
Super_Bowl_50: After a punt from both teams, Carolina got on track with a 9-play, 73-yard scoring drive. Newton completed 4 of 4 passes for 51 yards and rushed twice for 25 yards, while Jonathan Stewart finished the drive with a 1-yard touchdown run, cutting the score to 10–7 with 11:28 left in the second quarter. Later on, Broncos receiver Jordan Norwood received Brad Nortman's short 28-yard punt surrounded by Panthers players, but none of them attempted to make a tackle, apparently thinking Norwood had called a fair catch. Norwood had not done so, and with no resistance around him, he took off for a Super Bowl record 61-yard return before Mario Addison dragged him down on the Panthers 14-yard line. Despite Denver's excellent field position, they could not get the ball into the end zone, so McManus kicked a 33-yard field goal that increased their lead to 13–7.
```

#### Passage 5

- Chunk ID: `super_bowl_50-aad58c5e::c0`

```text
Super_Bowl_50: For the third straight season, the number one seeds from both conferences met in the Super Bowl. The Carolina Panthers became one of only ten teams to have completed a regular season with only one loss, and one of only six teams to have acquired a 15–1 record, while the Denver Broncos became one of four teams to have made eight appearances in the Super Bowl. The Broncos made their second Super Bowl appearance in three years, having reached Super Bowl XLVIII, while the Panthers made their second Super Bowl appearance in franchise history, their other appearance being Super Bowl XXXVIII. Coincidentally, both teams were coached by John Fox in their last Super Bowl appearance prior to Super Bowl 50.
```

#### Passage 6

- Chunk ID: `super_bowl_50-bcf54c0b::c0`

```text
Super_Bowl_50: After each team punted, Panthers quarterback Cam Newton appeared to complete a 24-yard pass Jerricho Cotchery, but the call was ruled an incompletion and upheld after a replay challenge. CBS analyst and retired referee Mike Carey stated he disagreed with the call and felt the review clearly showed the pass was complete. A few plays later, on 3rd-and-10 from the 15-yard line, linebacker Von Miller knocked the ball out of Newton's hands while sacking him, and Malik Jackson recovered it in the end zone for a Broncos touchdown, giving the team a 10–0 lead. This was the first fumble return touchdown in a Super Bowl since Super Bowl XXVIII at the end of the 1993 season.
```

#### Passage 7

- Chunk ID: `super_bowl_50-a533c800::c0`

```text
Super_Bowl_50: The Panthers seemed primed to score on their opening drive of the second half when Newton completed a 45-yard pass to Ted Ginn Jr. on the Denver 35-yard line on their second offensive play. But the Broncos defense halted the drive on the 26-yard line, and it ended with no points when Graham Gano hit the uprights on a 44-yard field goal attempt. After the miss, Manning completed a pair of passes to Emmanuel Sanders for gains of 25 and 22 yards, setting up McManus' 33-yard field goal that gave the Broncos a 16–7 lead. Carolina got off to another strong start after the kickoff, with Newton completing a 42-yard pass to Corey Brown. But once again they came up empty, this time as a result of a Newton pass that bounced off the hands of Ginn and was intercepted by safety T. J. Ward. Ward fumbled the ball during the return, but Trevathan recovered it to enable Denver to keep possession.
```

#### Passage 8

- Chunk ID: `super_bowl_50-31d37d05::c0`

```text
Super_Bowl_50: The Broncos defeated the Pittsburgh Steelers in the divisional round, 23–16, by scoring 11 points in the final three minutes of the game. They then beat the defending Super Bowl XLIX champion New England Patriots in the AFC Championship Game, 20–18, by intercepting a pass on New England's 2-point conversion attempt with 17 seconds left on the clock. Despite Manning's problems with interceptions during the season, he didn't throw any in their two playoff games.
```

## Case 9

- Question ID: `56de15dbcffd8e1900b4b5ca`
- Question: To where did Ethelred flee?
- Saved final passages: 8
- Chunk identifiers stored: yes
- First-retrieval passage text: not stored. No row below uses it.

### Claim 1

```text
Ethelred fled to Normandy in 1013, when he was forced from his kingdom by Sweyn Forkbeard.
```

Stored aggregate result from `squad_cond_C.jsonl` `claim_results`:

- Verdict `CONTRADICTED`; entailment 0.001982; contradiction 0.999234; uncertain `False`.
- Neutral probability: not stored. Per-premise probabilities: not stored. The premise that supplied each maximum: not stored.

Recomputed aggregate on these saved final passages, using `ClaimVerifier._premises` in joint mode and `ClaimVerifier._verdict` at 0.50. This recomputation is part of this diagnostic. It is not a new experiment result.

- Verdict `CONTRADICTED`; entailment 0.001982; contradiction 0.999234; confidence 0.999234.
- Maximum entailment is premise index 8 (Passage 8).
- Maximum contradiction is premise index 4 (Passage 4).
- Those two maxima come from different premises: yes.
- Recomputed aggregate matches the stored verdict and both scores within 1e-6: yes.

Pair-level rows use one saved final passage as the premise and this claim as the hypothesis. The verdict column applies the same 0.50 rule to that pair alone. It is not the verdict stored by Condition C.

| Passage | Chunk ID | Entailment | Contradiction | Neutral | Pair verdict | Differs from stored aggregate? | Role in recomputed aggregate |
|---|---|---:|---:|---:|---|---|---|
| P1 | `normans-9b8d823d::c0` | 0.000785 | 0.000763 | 0.998452 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P2 | `huguenot-cba1c27b::c0` | 0.000624 | 0.007141 | 0.992235 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P3 | `normans-694b5e40::c0` | 0.000267 | 0.076393 | 0.923340 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P4 | `huguenot-488d1c49::c0` | 0.000007 | 0.999234 | 0.000758 | `CONTRADICTED` | No | max contradiction in the joint premise list |
| P5 | `newcastle_upon_tyne-9598a624::c0` | 0.000043 | 0.965020 | 0.034937 | `CONTRADICTED` | No |  |
| P6 | `normans-f9f1ea37::c0` | 0.000195 | 0.001401 | 0.998404 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P7 | `normans-d963cb53::c0` | 0.000133 | 0.934495 | 0.065372 | `CONTRADICTED` | No |  |
| P8 | `normans-0b1edd8d::c0` | 0.001982 | 0.027960 | 0.970058 | `INSUFFICIENT_EVIDENCE` | Yes | max entailment in the joint premise list |

Verifier-constructed joint premise, not a retrieved passage: first 320 words of the saved final passages joined in order, capped at 320 words. Pair verdict on this constructed premise alone: `INSUFFICIENT_EVIDENCE` (entailment 0.001356, contradiction 0.004521, neutral 0.994124). This pair verdict differs from the stored aggregate: yes.

```text
Normans: The Normans were in contact with England from an early date. Not only were their original Viking brethren still ravaging the English coasts, they occupied most of the important ports opposite England across the English Channel. This relationship eventually produced closer ties of blood through the marriage of Emma, sister of Duke Richard II of Normandy, and King Ethelred II of England. Because of this, Ethelred fled to Normandy in 1013, when he was forced from his kingdom by Sweyn Forkbeard. His stay in Normandy (until 1016) influenced him and his sons by Emma, who stayed in Normandy after Cnut the Great's conquest of the isle. Huguenot: Other evidence of the Walloons and Huguenots in Canterbury includes a block of houses in Turnagain Lane, where weavers' windows survive on the top floor, as many Huguenots worked as weavers. The Weavers, a half-timbered house by the river, was the site of a weaving school from the late 16th century to about 1830. (It has been adapted as a restaurant—see illustration above. The house derives its name from a weaving school which was moved there in the last years of the 19th century, reviving an earlier use.) Others refugees practised the variety of occupations necessary to sustain the community as distinct from the indigenous population. Such economic separation was the condition of the refugees' initial acceptance in the City. They also settled elsewhere in Kent, particularly Sandwich, Faversham and Maidstone—towns in which there used to be refugee churches. Normans: Various princes of the Holy Land arrived in Limassol at the same time, in particular Guy de Lusignan. All declared their support for Richard provided that he support Guy against his rival Conrad of Montferrat. The local barons abandoned Isaac, who considered making peace with Richard, joining him on the crusade, and offering his daughter in marriage to the person named by Richard. But Isaac changed his mind and tried to escape.
```

### Exact saved final passages

These strings are the Condition C `contexts` field. Passage numbers match the table above.

#### Passage 1

- Chunk ID: `normans-9b8d823d::c0`

```text
Normans: The Normans were in contact with England from an early date. Not only were their original Viking brethren still ravaging the English coasts, they occupied most of the important ports opposite England across the English Channel. This relationship eventually produced closer ties of blood through the marriage of Emma, sister of Duke Richard II of Normandy, and King Ethelred II of England. Because of this, Ethelred fled to Normandy in 1013, when he was forced from his kingdom by Sweyn Forkbeard. His stay in Normandy (until 1016) influenced him and his sons by Emma, who stayed in Normandy after Cnut the Great's conquest of the isle.
```

#### Passage 2

- Chunk ID: `huguenot-cba1c27b::c0`

```text
Huguenot: Other evidence of the Walloons and Huguenots in Canterbury includes a block of houses in Turnagain Lane, where weavers' windows survive on the top floor, as many Huguenots worked as weavers. The Weavers, a half-timbered house by the river, was the site of a weaving school from the late 16th century to about 1830. (It has been adapted as a restaurant—see illustration above. The house derives its name from a weaving school which was moved there in the last years of the 19th century, reviving an earlier use.) Others refugees practised the variety of occupations necessary to sustain the community as distinct from the indigenous population. Such economic separation was the condition of the refugees' initial acceptance in the City. They also settled elsewhere in Kent, particularly Sandwich, Faversham and Maidstone—towns in which there used to be refugee churches.
```

#### Passage 3

- Chunk ID: `normans-694b5e40::c0`

```text
Normans: Various princes of the Holy Land arrived in Limassol at the same time, in particular Guy de Lusignan. All declared their support for Richard provided that he support Guy against his rival Conrad of Montferrat. The local barons abandoned Isaac, who considered making peace with Richard, joining him on the crusade, and offering his daughter in marriage to the person named by Richard. But Isaac changed his mind and tried to escape. Richard then proceeded to conquer the whole island, his troops being led by Guy de Lusignan. Isaac surrendered and was confined with silver chains, because Richard had promised that he would not place him in irons. By 1 June, Richard had conquered the whole island. His exploit was well publicized and contributed to his reputation; he also derived significant financial gains from the conquest of the island. Richard left for Acre on 5 June, with his allies. Before his departure, he named two of his Norman generals, Richard de Camville and Robert de Thornham, as governors of Cyprus.
```

#### Passage 4

- Chunk ID: `huguenot-488d1c49::c0`

```text
Huguenot: In 1564 a group of Norman Huguenots under the leadership of Jean Ribault established the small colony of Fort Caroline on the banks of the St. Johns River in what is today Jacksonville, Florida. The effort was the first at any permanent European settlement in the present-day continental United States, but survived only a short time. A September 1565 French naval attack against the new Spanish colony at St. Augustine failed when its ships were hit by a hurricane on their way to the Spanish encampment at Fort Matanzas. Hundreds of French soldiers were stranded and surrendered to the numerically inferior Spanish forces led by Pedro Menendez. Menendez proceeded to massacre the defenseless Huguenots, after which he wiped out the Fort Caroline garrison.
```

#### Passage 5

- Chunk ID: `newcastle_upon_tyne-9598a624::c0`

```text
Newcastle_upon_Tyne: During the English Civil War, the North declared for the King. In a bid to gain Newcastle and the Tyne, Cromwell's allies, the Scots, captured the town of Newburn. In 1644 the Scots then captured the reinforced fortification on the Lawe in South Shields following a siege. In 1644 the city was then besieged for many months and was eventually stormed ('with roaring drummes') and sacked by Cromwell's allies. The grateful King bestowed the motto "Fortiter Defendit Triumphans" ("Triumphing by a brave defence") upon the town. Charles I was imprisoned in Newcastle by the Scots in 1646–7.
```

#### Passage 6

- Chunk ID: `normans-f9f1ea37::c0`

```text
Normans: Normans came into Scotland, building castles and founding noble families who would provide some future kings, such as Robert the Bruce, as well as founding a considerable number of the Scottish clans. King David I of Scotland, whose elder brother Alexander I had married Sybilla of Normandy, was instrumental in introducing Normans and Norman culture to Scotland, part of the process some scholars call the "Davidian Revolution". Having spent time at the court of Henry I of England (married to David's sister Maud of Scotland), and needing them to wrestle the kingdom from his half-brother Máel Coluim mac Alaxandair, David had to reward many with lands. The process was continued under David's successors, most intensely of all under William the Lion. The Norman-derived feudal system was applied in varying degrees to most of Scotland. Scottish families of the names Bruce, Gray, Ramsay, Fraser, Ogilvie, Montgomery, Sinclair, Pollock, Burnard, Douglas and Gordon to name but a few, and including the later royal House of Stewart, can all be traced back to Norman ancestry.
```

#### Passage 7

- Chunk ID: `normans-d963cb53::c0`

```text
Normans: The legendary religious zeal of the Normans was exercised in religious wars long before the First Crusade carved out a Norman principality in Antioch. They were major foreign participants in the Reconquista in Iberia. In 1018, Roger de Tosny travelled to the Iberian Peninsula to carve out a state for himself from Moorish lands, but failed. In 1064, during the War of Barbastro, William of Montreuil led the papal army and took a huge booty.
```

#### Passage 8

- Chunk ID: `normans-0b1edd8d::c0`

```text
Normans: Eventually, the Normans merged with the natives, combining languages and traditions. In the course of the Hundred Years' War, the Norman aristocracy often identified themselves as English. The Anglo-Norman language became distinct from the Latin language, something that was the subject of some humour by Geoffrey Chaucer. The Anglo-Norman language was eventually absorbed into the Anglo-Saxon language of their subjects (see Old English) and influenced it, helping (along with the Norse language of the earlier Anglo-Norse settlers and the Latin used by the church) in the development of Middle English. It in turn evolved into Modern English.
```

## Case 10

- Question ID: `56e0d402231d4119001ac3fc`
- Question: In what year did Tesla go to Budapest?
- Saved final passages: 8
- Chunk identifiers stored: yes
- First-retrieval passage text: not stored. No row below uses it.

### Claim 1

```text
In 1881, Tesla moved to Budapest to work under Ferenc Puskás at a telegraph company
```

Stored aggregate result from `squad_cond_C.jsonl` `claim_results`:

- Verdict `CONTRADICTED`; entailment 0.000237; contradiction 0.999739; uncertain `False`.
- Neutral probability: not stored. Per-premise probabilities: not stored. The premise that supplied each maximum: not stored.

Recomputed aggregate on these saved final passages, using `ClaimVerifier._premises` in joint mode and `ClaimVerifier._verdict` at 0.50. This recomputation is part of this diagnostic. It is not a new experiment result.

- Verdict `CONTRADICTED`; entailment 0.000237; contradiction 0.999739; confidence 0.999739.
- Maximum entailment is premise index 0 (joint premise attributed to passages 1, 2, 3, 4, 5).
- Maximum contradiction is premise index 3 (Passage 3).
- Those two maxima come from different premises: yes.
- Recomputed aggregate matches the stored verdict and both scores within 1e-6: yes.

Pair-level rows use one saved final passage as the premise and this claim as the hypothesis. The verdict column applies the same 0.50 rule to that pair alone. It is not the verdict stored by Condition C.

| Passage | Chunk ID | Entailment | Contradiction | Neutral | Pair verdict | Differs from stored aggregate? | Role in recomputed aggregate |
|---|---|---:|---:|---:|---|---|---|
| P1 | `nikola_tesla-35d59d31::c0` | 0.000082 | 0.009408 | 0.990510 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P2 | `nikola_tesla-d2acd518::c0` | 0.000087 | 0.988025 | 0.011888 | `CONTRADICTED` | No |  |
| P3 | `nikola_tesla-6efdeead::c0` | 0.000009 | 0.999739 | 0.000252 | `CONTRADICTED` | No | max contradiction in the joint premise list |
| P4 | `nikola_tesla-a955be31::c0` | 0.000030 | 0.972323 | 0.027647 | `CONTRADICTED` | No |  |
| P5 | `nikola_tesla-ea98be57::c0` | 0.000144 | 0.560242 | 0.439613 | `CONTRADICTED` | No |  |
| P6 | `nikola_tesla-e8bb43aa::c0` | 0.000023 | 0.990319 | 0.009658 | `CONTRADICTED` | No |  |
| P7 | `nikola_tesla-2cba8723::c0` | 0.000017 | 0.999479 | 0.000503 | `CONTRADICTED` | No |  |
| P8 | `nikola_tesla-083cab5b::c0` | 0.000028 | 0.984566 | 0.015406 | `CONTRADICTED` | No |  |

Verifier-constructed joint premise, not a retrieved passage: first 320 words of the saved final passages joined in order, capped at 320 words. Pair verdict on this constructed premise alone: `INSUFFICIENT_EVIDENCE` (entailment 0.000237, contradiction 0.004651, neutral 0.995112). This pair verdict differs from the stored aggregate: yes.

```text
Nikola_Tesla: In 1881, Tesla moved to Budapest to work under Ferenc Puskás at a telegraph company, the Budapest Telephone Exchange. Upon arrival, Tesla realized that the company, then under construction, was not functional, so he worked as a draftsman in the Central Telegraph Office instead. Within a few months, the Budapest Telephone Exchange became functional and Tesla was allocated the chief electrician position. During his employment, Tesla made many improvements to the Central Station equipment and claimed to have perfected a telephone repeater or amplifier, which was never patented nor publicly described. Nikola_Tesla: Before World War I, Tesla sought overseas investors. After the war started, Tesla lost the funding he was receiving from his patents in European countries. Eventually, he sold Wardenclyffe for $20,000 ($472,500 in today's dollars). In 1917, around the time that the Wardenclyffe Tower was demolished by Boldt to make the land a more viable real estate asset, Tesla received AIEE's highest honor, the Edison Medal. Nikola_Tesla: In 1952, following pressure from Tesla's nephew, Sava Kosanović, Tesla's entire estate was shipped to Belgrade in 80 trunks marked N.T. In 1957, Kosanović's secretary Charlotte Muzar transported Tesla's ashes from the United States to Belgrade. The ashes are displayed in a gold-plated sphere on a marble pedestal in the Nikola Tesla Museum. Nikola_Tesla: Tesla went on to pursue his ideas of wireless lighting and electricity distribution in his high-voltage, high-frequency power experiments in New York and Colorado Springs, and made early (1893) pronouncements on the possibility of wireless communication with his devices. He tried to put these ideas to practical use in an ill-fated attempt at intercontinental wireless transmission, his unfinished Wardenclyffe Tower project. In his lab he also conducted a range of experiments with mechanical oscillators/generators, electrical discharge tubes, and early X-ray imaging. He also built a wireless controlled boat, one of the first ever exhibited. Nikola_Tesla: Tesla was renowned for his achievements and showmanship, eventually earning him
```

### Exact saved final passages

These strings are the Condition C `contexts` field. Passage numbers match the table above.

#### Passage 1

- Chunk ID: `nikola_tesla-35d59d31::c0`

```text
Nikola_Tesla: In 1881, Tesla moved to Budapest to work under Ferenc Puskás at a telegraph company, the Budapest Telephone Exchange. Upon arrival, Tesla realized that the company, then under construction, was not functional, so he worked as a draftsman in the Central Telegraph Office instead. Within a few months, the Budapest Telephone Exchange became functional and Tesla was allocated the chief electrician position. During his employment, Tesla made many improvements to the Central Station equipment and claimed to have perfected a telephone repeater or amplifier, which was never patented nor publicly described.
```

#### Passage 2

- Chunk ID: `nikola_tesla-d2acd518::c0`

```text
Nikola_Tesla: Before World War I, Tesla sought overseas investors. After the war started, Tesla lost the funding he was receiving from his patents in European countries. Eventually, he sold Wardenclyffe for $20,000 ($472,500 in today's dollars). In 1917, around the time that the Wardenclyffe Tower was demolished by Boldt to make the land a more viable real estate asset, Tesla received AIEE's highest honor, the Edison Medal.
```

#### Passage 3

- Chunk ID: `nikola_tesla-6efdeead::c0`

```text
Nikola_Tesla: In 1952, following pressure from Tesla's nephew, Sava Kosanović, Tesla's entire estate was shipped to Belgrade in 80 trunks marked N.T. In 1957, Kosanović's secretary Charlotte Muzar transported Tesla's ashes from the United States to Belgrade. The ashes are displayed in a gold-plated sphere on a marble pedestal in the Nikola Tesla Museum.
```

#### Passage 4

- Chunk ID: `nikola_tesla-a955be31::c0`

```text
Nikola_Tesla: Tesla went on to pursue his ideas of wireless lighting and electricity distribution in his high-voltage, high-frequency power experiments in New York and Colorado Springs, and made early (1893) pronouncements on the possibility of wireless communication with his devices. He tried to put these ideas to practical use in an ill-fated attempt at intercontinental wireless transmission, his unfinished Wardenclyffe Tower project. In his lab he also conducted a range of experiments with mechanical oscillators/generators, electrical discharge tubes, and early X-ray imaging. He also built a wireless controlled boat, one of the first ever exhibited.
```

#### Passage 5

- Chunk ID: `nikola_tesla-ea98be57::c0`

```text
Nikola_Tesla: Tesla was renowned for his achievements and showmanship, eventually earning him a reputation in popular culture as an archetypal "mad scientist". His patents earned him a considerable amount of money, much of which was used to finance his own projects with varying degrees of success.:121,154 He lived most of his life in a series of New York hotels, through his retirement. Tesla died on 7 January 1943. His work fell into relative obscurity after his death, but in 1960 the General Conference on Weights and Measures named the SI unit of magnetic flux density the tesla in his honor. There has been a resurgence in popular interest in Tesla since the 1990s.
```

#### Passage 6

- Chunk ID: `nikola_tesla-e8bb43aa::c0`

```text
Nikola_Tesla: On 30 July 1891, at the age of 35, Tesla became a naturalized citizen of the United States, and established his South Fifth Avenue laboratory, and later another at 46 E. Houston Street, in New York. He lit electric lamps wirelessly at both locations, demonstrating the potential of wireless power transmission. In the same year, he patented the Tesla coil.
```

#### Passage 7

- Chunk ID: `nikola_tesla-2cba8723::c0`

```text
Nikola_Tesla: In 1935, in an annual birthday celebration interview, Tesla announced a method of transmitting mechanical energy with minimal loss over any terrestrial distance, a related new means of communication, and a method of accurately determining the location of underground mineral deposits.
```

#### Passage 8

- Chunk ID: `nikola_tesla-083cab5b::c0`

```text
Nikola_Tesla: Nikola Tesla (Serbian Cyrillic: Никола Тесла; 10 July 1856 – 7 January 1943) was a Serbian American inventor, electrical engineer, mechanical engineer, physicist, and futurist best known for his contributions to the design of the modern alternating current (AC) electricity supply system.
```

## Case 11

- Question ID: `56be8e613aeaaa14008c90d2`
- Question: What day was the game played on?
- Saved final passages: 8
- Chunk identifiers stored: yes
- First-retrieval passage text: not stored. No row below uses it.

### Claim 1

```text
Super_Bowl_50 was played on February 7, 2016, at Levi's Stadium in the San Francisco Bay Area at Santa Clara, California.
```

Stored aggregate result from `squad_cond_C.jsonl` `claim_results`:

- Verdict `CONTRADICTED`; entailment 0.002024; contradiction 0.994615; uncertain `False`.
- Neutral probability: not stored. Per-premise probabilities: not stored. The premise that supplied each maximum: not stored.

Recomputed aggregate on these saved final passages, using `ClaimVerifier._premises` in joint mode and `ClaimVerifier._verdict` at 0.50. This recomputation is part of this diagnostic. It is not a new experiment result.

- Verdict `CONTRADICTED`; entailment 0.002024; contradiction 0.994615; confidence 0.994615.
- Maximum entailment is premise index 1 (Passage 1).
- Maximum contradiction is premise index 4 (Passage 4).
- Those two maxima come from different premises: yes.
- Recomputed aggregate matches the stored verdict and both scores within 1e-6: yes.

Pair-level rows use one saved final passage as the premise and this claim as the hypothesis. The verdict column applies the same 0.50 rule to that pair alone. It is not the verdict stored by Condition C.

| Passage | Chunk ID | Entailment | Contradiction | Neutral | Pair verdict | Differs from stored aggregate? | Role in recomputed aggregate |
|---|---|---:|---:|---:|---|---|---|
| P1 | `super_bowl_50-6b0af9df::c0` | 0.002024 | 0.002835 | 0.995141 | `INSUFFICIENT_EVIDENCE` | Yes | max entailment in the joint premise list |
| P2 | `super_bowl_50-68884356::c0` | 0.000309 | 0.993734 | 0.005957 | `CONTRADICTED` | No |  |
| P3 | `super_bowl_50-d6975221::c0` | 0.000129 | 0.975513 | 0.024358 | `CONTRADICTED` | No |  |
| P4 | `super_bowl_50-7d0d0b85::c0` | 0.000281 | 0.994615 | 0.005104 | `CONTRADICTED` | No | max contradiction in the joint premise list |
| P5 | `american_broadcasting_company-2c308d98::c0` | 0.000181 | 0.002938 | 0.996881 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P6 | `super_bowl_50-f1b96eb2::c0` | 0.000711 | 0.015077 | 0.984212 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P7 | `super_bowl_50-aad58c5e::c0` | 0.000148 | 0.003789 | 0.996063 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P8 | `super_bowl_50-a533c800::c0` | 0.000533 | 0.018211 | 0.981256 | `INSUFFICIENT_EVIDENCE` | Yes |  |

Verifier-constructed joint premise, not a retrieved passage: first 320 words of the saved final passages joined in order, capped at 320 words. Pair verdict on this constructed premise alone: `INSUFFICIENT_EVIDENCE` (entailment 0.000880, contradiction 0.006249, neutral 0.992871). This pair verdict differs from the stored aggregate: yes.

```text
Super_Bowl_50: Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24–10 to earn their third Super Bowl title. The game was played on February 7, 2016, at Levi's Stadium in the San Francisco Bay Area at Santa Clara, California. As this was the 50th Super Bowl, the league emphasized the "golden anniversary" with various gold-themed initiatives, as well as temporarily suspending the tradition of naming each Super Bowl game with Roman numerals (under which the game would have been known as "Super Bowl L"), so that the logo could prominently feature the Arabic numerals 50. Super_Bowl_50: The game's media day, which was typically held on the Tuesday afternoon prior to the game, was moved to the Monday evening and re-branded as Super Bowl Opening Night. The event was held on February 1, 2016 at SAP Center in San Jose. Alongside the traditional media availabilities, the event featured an opening ceremony with player introductions on a replica of the Golden Gate Bridge. Super_Bowl_50: The league announced on October 16, 2012, that the two finalists were Sun Life Stadium and Levi's Stadium. The South Florida/Miami area has previously hosted the event 10 times (tied for most with New Orleans), with the most recent one being Super Bowl XLIV in 2010. The San Francisco Bay Area last hosted in 1985 (Super Bowl XIX), held at Stanford Stadium in Stanford, California, won by the home team 49ers. The Miami bid depended on whether the stadium underwent renovations. However, on May 3, 2013, the Florida legislature refused to approve the funding plan to pay for the renovations, dealing a significant blow to Miami's chances. Super_Bowl_50: On May 21, 2013, NFL owners at their spring meetings in Boston voted and awarded the game to Levi's Stadium.
```

### Exact saved final passages

These strings are the Condition C `contexts` field. Passage numbers match the table above.

#### Passage 1

- Chunk ID: `super_bowl_50-6b0af9df::c0`

```text
Super_Bowl_50: Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated the National Football Conference (NFC) champion Carolina Panthers 24–10 to earn their third Super Bowl title. The game was played on February 7, 2016, at Levi's Stadium in the San Francisco Bay Area at Santa Clara, California. As this was the 50th Super Bowl, the league emphasized the "golden anniversary" with various gold-themed initiatives, as well as temporarily suspending the tradition of naming each Super Bowl game with Roman numerals (under which the game would have been known as "Super Bowl L"), so that the logo could prominently feature the Arabic numerals 50.
```

#### Passage 2

- Chunk ID: `super_bowl_50-68884356::c0`

```text
Super_Bowl_50: The game's media day, which was typically held on the Tuesday afternoon prior to the game, was moved to the Monday evening and re-branded as Super Bowl Opening Night. The event was held on February 1, 2016 at SAP Center in San Jose. Alongside the traditional media availabilities, the event featured an opening ceremony with player introductions on a replica of the Golden Gate Bridge.
```

#### Passage 3

- Chunk ID: `super_bowl_50-d6975221::c0`

```text
Super_Bowl_50: The league announced on October 16, 2012, that the two finalists were Sun Life Stadium and Levi's Stadium. The South Florida/Miami area has previously hosted the event 10 times (tied for most with New Orleans), with the most recent one being Super Bowl XLIV in 2010. The San Francisco Bay Area last hosted in 1985 (Super Bowl XIX), held at Stanford Stadium in Stanford, California, won by the home team 49ers. The Miami bid depended on whether the stadium underwent renovations. However, on May 3, 2013, the Florida legislature refused to approve the funding plan to pay for the renovations, dealing a significant blow to Miami's chances.
```

#### Passage 4

- Chunk ID: `super_bowl_50-7d0d0b85::c0`

```text
Super_Bowl_50: On May 21, 2013, NFL owners at their spring meetings in Boston voted and awarded the game to Levi's Stadium. The $1.2 billion stadium opened in 2014. It is the first Super Bowl held in the San Francisco Bay Area since Super Bowl XIX in 1985, and the first in California since Super Bowl XXXVII took place in San Diego in 2003.
```

#### Passage 5

- Chunk ID: `american_broadcasting_company-2c308d98::c0`

```text
American_Broadcasting_Company: In 1970, ABC debuted Monday Night Football as part of its Monday prime time schedule; the program became a hit for the network and served as the National Football League (NFL)'s premier game of the week until 2006, when Sunday Night Football, which moved to NBC that year as part of a broadcast deal that in turn saw MNF move to ESPN, took over as the league's marquee game. According to Goldenson, Monday Night Football helped earn ABC regularly score an audience share of 15%–16%; ABC Sports managed the budget for the Monday night time slot to reallocate the weekly budget for ABC's prime time schedule to just six days, as opposed to seven on competing networks. 1970 also saw the premieres of several soap operas including the long-running All My Children, which ran on the network for 41 years.
```

#### Passage 6

- Chunk ID: `super_bowl_50-f1b96eb2::c0`

```text
Super_Bowl_50: The Panthers finished the regular season with a 15–1 record, and quarterback Cam Newton was named the NFL Most Valuable Player (MVP). They defeated the Arizona Cardinals 49–15 in the NFC Championship Game and advanced to their second Super Bowl appearance since the franchise was founded in 1995. The Broncos finished the regular season with a 12–4 record, and denied the New England Patriots a chance to defend their title from Super Bowl XLIX by defeating them 20–18 in the AFC Championship Game. They joined the Patriots, Dallas Cowboys, and Pittsburgh Steelers as one of four teams that have made eight appearances in the Super Bowl.
```

#### Passage 7

- Chunk ID: `super_bowl_50-aad58c5e::c0`

```text
Super_Bowl_50: For the third straight season, the number one seeds from both conferences met in the Super Bowl. The Carolina Panthers became one of only ten teams to have completed a regular season with only one loss, and one of only six teams to have acquired a 15–1 record, while the Denver Broncos became one of four teams to have made eight appearances in the Super Bowl. The Broncos made their second Super Bowl appearance in three years, having reached Super Bowl XLVIII, while the Panthers made their second Super Bowl appearance in franchise history, their other appearance being Super Bowl XXXVIII. Coincidentally, both teams were coached by John Fox in their last Super Bowl appearance prior to Super Bowl 50.
```

#### Passage 8

- Chunk ID: `super_bowl_50-a533c800::c0`

```text
Super_Bowl_50: The Panthers seemed primed to score on their opening drive of the second half when Newton completed a 45-yard pass to Ted Ginn Jr. on the Denver 35-yard line on their second offensive play. But the Broncos defense halted the drive on the 26-yard line, and it ended with no points when Graham Gano hit the uprights on a 44-yard field goal attempt. After the miss, Manning completed a pair of passes to Emmanuel Sanders for gains of 25 and 22 yards, setting up McManus' 33-yard field goal that gave the Broncos a 16–7 lead. Carolina got off to another strong start after the kickoff, with Newton completing a 42-yard pass to Corey Brown. But once again they came up empty, this time as a result of a Newton pass that bounced off the hands of Ginn and was intercepted by safety T. J. Ward. Ward fumbled the ball during the return, but Trevathan recovered it to enable Denver to keep possession.
```

## Case 12

- Question ID: `56bebde53aeaaa14008c9338`
- Question: In what city is SAP Center located?
- Saved final passages: 8
- Chunk identifiers stored: yes
- First-retrieval passage text: not stored. No row below uses it.

### Claim 1

```text
SAP Center is located in San Jose
```

Stored aggregate result from `squad_cond_C.jsonl` `claim_results`:

- Verdict `CONTRADICTED`; entailment 0.127165; contradiction 0.999301; uncertain `False`.
- Neutral probability: not stored. Per-premise probabilities: not stored. The premise that supplied each maximum: not stored.

Recomputed aggregate on these saved final passages, using `ClaimVerifier._premises` in joint mode and `ClaimVerifier._verdict` at 0.50. This recomputation is part of this diagnostic. It is not a new experiment result.

- Verdict `CONTRADICTED`; entailment 0.127165; contradiction 0.999301; confidence 0.999301.
- Maximum entailment is premise index 2 (Passage 2).
- Maximum contradiction is premise index 7 (Passage 7).
- Those two maxima come from different premises: yes.
- Recomputed aggregate matches the stored verdict and both scores within 1e-6: yes.

Pair-level rows use one saved final passage as the premise and this claim as the hypothesis. The verdict column applies the same 0.50 rule to that pair alone. It is not the verdict stored by Condition C.

| Passage | Chunk ID | Entailment | Contradiction | Neutral | Pair verdict | Differs from stored aggregate? | Role in recomputed aggregate |
|---|---|---:|---:|---:|---|---|---|
| P1 | `university_of_chicago-5d00934f::c0` | 0.000040 | 0.969054 | 0.030906 | `CONTRADICTED` | No |  |
| P2 | `super_bowl_50-68884356::c0` | 0.127165 | 0.000889 | 0.871947 | `INSUFFICIENT_EVIDENCE` | Yes | max entailment in the joint premise list |
| P3 | `warsaw-251afb78::c0` | 0.000750 | 0.028900 | 0.970350 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P4 | `victoria_australia-85ec962c::c0` | 0.000151 | 0.001828 | 0.998022 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P5 | `amazon_rainforest-cf1362c1::c0` | 0.001470 | 0.021986 | 0.976544 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P6 | `university_of_chicago-db8c3287::c0` | 0.000035 | 0.980180 | 0.019785 | `CONTRADICTED` | No |  |
| P7 | `university_of_chicago-862decf2::c0` | 0.000020 | 0.999301 | 0.000679 | `CONTRADICTED` | No | max contradiction in the joint premise list |
| P8 | `university_of_chicago-140180f8::c0` | 0.000139 | 0.857530 | 0.142330 | `CONTRADICTED` | No |  |

Verifier-constructed joint premise, not a retrieved passage: first 320 words of the saved final passages joined in order, capped at 320 words. Pair verdict on this constructed premise alone: `INSUFFICIENT_EVIDENCE` (entailment 0.000305, contradiction 0.004665, neutral 0.995030). This pair verdict differs from the stored aggregate: yes.

```text
University_of_Chicago: The University of Chicago also maintains facilities apart from its main campus. The university's Booth School of Business maintains campuses in Singapore, London, and the downtown Streeterville neighborhood of Chicago. The Center in Paris, a campus located on the left bank of the Seine in Paris, hosts various undergraduate and graduate study programs. In fall 2010, the University of Chicago also opened a center in Beijing, near Renmin University's campus in Haidian District. The most recent additions are a center in New Delhi, India, which opened in 2014, and a center in Hong Kong which opened in 2015. Super_Bowl_50: The game's media day, which was typically held on the Tuesday afternoon prior to the game, was moved to the Monday evening and re-branded as Super Bowl Opening Night. The event was held on February 1, 2016 at SAP Center in San Jose. Alongside the traditional media availabilities, the event featured an opening ceremony with player introductions on a replica of the Golden Gate Bridge. Warsaw: Warsaw (Polish: Warszawa [varˈʂava] ( listen); see also other names) is the capital and largest city of Poland. It stands on the Vistula River in east-central Poland, roughly 260 kilometres (160 mi) from the Baltic Sea and 300 kilometres (190 mi) from the Carpathian Mountains. Its population is estimated at 1.740 million residents within a greater metropolitan area of 2.666 million residents, which makes Warsaw the 9th most-populous capital city in the European Union. The city limits cover 516.9 square kilometres (199.6 sq mi), while the metropolitan area covers 6,100.43 square kilometres (2,355.39 sq mi). Victoria_(Australia): Victoria is the centre of dairy farming in Australia. It is home to 60% of Australia's 3 million dairy cattle and produces nearly two-thirds of the nation's milk, almost 6.4 billion litres. The state also has 2.4 million beef cattle, with more than 2.2 million cattle and calves slaughtered each year. In 2003–04, Victorian commercial fishing crews and
```

### Exact saved final passages

These strings are the Condition C `contexts` field. Passage numbers match the table above.

#### Passage 1

- Chunk ID: `university_of_chicago-5d00934f::c0`

```text
University_of_Chicago: The University of Chicago also maintains facilities apart from its main campus. The university's Booth School of Business maintains campuses in Singapore, London, and the downtown Streeterville neighborhood of Chicago. The Center in Paris, a campus located on the left bank of the Seine in Paris, hosts various undergraduate and graduate study programs. In fall 2010, the University of Chicago also opened a center in Beijing, near Renmin University's campus in Haidian District. The most recent additions are a center in New Delhi, India, which opened in 2014, and a center in Hong Kong which opened in 2015.
```

#### Passage 2

- Chunk ID: `super_bowl_50-68884356::c0`

```text
Super_Bowl_50: The game's media day, which was typically held on the Tuesday afternoon prior to the game, was moved to the Monday evening and re-branded as Super Bowl Opening Night. The event was held on February 1, 2016 at SAP Center in San Jose. Alongside the traditional media availabilities, the event featured an opening ceremony with player introductions on a replica of the Golden Gate Bridge.
```

#### Passage 3

- Chunk ID: `warsaw-251afb78::c0`

```text
Warsaw: Warsaw (Polish: Warszawa [varˈʂava] ( listen); see also other names) is the capital and largest city of Poland. It stands on the Vistula River in east-central Poland, roughly 260 kilometres (160 mi) from the Baltic Sea and 300 kilometres (190 mi) from the Carpathian Mountains. Its population is estimated at 1.740 million residents within a greater metropolitan area of 2.666 million residents, which makes Warsaw the 9th most-populous capital city in the European Union. The city limits cover 516.9 square kilometres (199.6 sq mi), while the metropolitan area covers 6,100.43 square kilometres (2,355.39 sq mi).
```

#### Passage 4

- Chunk ID: `victoria_australia-85ec962c::c0`

```text
Victoria_(Australia): Victoria is the centre of dairy farming in Australia. It is home to 60% of Australia's 3 million dairy cattle and produces nearly two-thirds of the nation's milk, almost 6.4 billion litres. The state also has 2.4 million beef cattle, with more than 2.2 million cattle and calves slaughtered each year. In 2003–04, Victorian commercial fishing crews and aquaculture industry produced 11,634 tonnes of seafood valued at nearly A$109 million. Blacklipped abalone is the mainstay of the catch, bringing in A$46 million, followed by southern rock lobster worth A$13.7 million. Most abalone and rock lobster is exported to Asia.
```

#### Passage 5

- Chunk ID: `amazon_rainforest-cf1362c1::c0`

```text
Amazon_rainforest: The Amazon rainforest (Portuguese: Floresta Amazônica or Amazônia; Spanish: Selva Amazónica, Amazonía or usually Amazonia; French: Forêt amazonienne; Dutch: Amazoneregenwoud), also known in English as Amazonia or the Amazon Jungle, is a moist broadleaf forest that covers most of the Amazon basin of South America. This basin encompasses 7,000,000 square kilometres (2,700,000 sq mi), of which 5,500,000 square kilometres (2,100,000 sq mi) are covered by the rainforest. This region includes territory belonging to nine nations. The majority of the forest is contained within Brazil, with 60% of the rainforest, followed by Peru with 13%, Colombia with 10%, and with minor amounts in Venezuela, Ecuador, Bolivia, Guyana, Suriname and French Guiana. States or departments in four nations contain "Amazonas" in their names. The Amazon represents over half of the planet's remaining rainforests, and comprises the largest and most biodiverse tract of tropical rainforest in the world, with an estimated 390 billion individual trees divided into 16,000 species.
```

#### Passage 6

- Chunk ID: `university_of_chicago-db8c3287::c0`

```text
University_of_Chicago: University of Chicago scholars have played a major role in the development of various academic disciplines, including: the Chicago school of economics, the Chicago school of sociology, the law and economics movement in legal analysis, the Chicago school of literary criticism, the Chicago school of religion, and the behavioralism school of political science. Chicago's physics department helped develop the world's first man-made, self-sustaining nuclear reaction beneath the university's Stagg Field. Chicago's research pursuits have been aided by unique affiliations with world-renowned institutions like the nearby Fermilab and Argonne National Laboratory, as well as the Marine Biological Laboratory. The university is also home to the University of Chicago Press, the largest university press in the United States. With an estimated completion date of 2020, the Barack Obama Presidential Center will be housed at the university and include both the Obama presidential library and offices of the Obama Foundation.
```

#### Passage 7

- Chunk ID: `university_of_chicago-862decf2::c0`

```text
University_of_Chicago: The University of Chicago was created and incorporated as a coeducational, secular institution in 1890 by the American Baptist Education Society and a donation from oil magnate and philanthropist John D. Rockefeller on land donated by Marshall Field. While the Rockefeller donation provided money for academic operations and long-term endowment, it was stipulated that such money could not be used for buildings. The original physical campus was financed by donations from wealthy Chicagoans like Silas B. Cobb who provided the funds for the campus' first building, Cobb Lecture Hall, and matched Marshall Field's pledge of $100,000. Other early benefactors included businessmen Charles L. Hutchinson (trustee, treasurer and donor of Hutchinson Commons), Martin A. Ryerson (president of the board of trustees and donor of the Ryerson Physical Laboratory) Adolphus Clay Bartlett and Leon Mandel, who funded the construction of the gymnasium and assembly hall, and George C. Walker of the Walker Museum, a relative of Cobb who encouraged his inaugural donation for facilities.
```

#### Passage 8

- Chunk ID: `university_of_chicago-140180f8::c0`

```text
University_of_Chicago: In 1929, the university's fifth president, Robert Maynard Hutchins, took office; the university underwent many changes during his 24-year tenure. Hutchins eliminated varsity football from the university in an attempt to emphasize academics over athletics, instituted the undergraduate college's liberal-arts curriculum known as the Common Core, and organized the university's graduate work into its current[when?] four divisions. In 1933, Hutchins proposed an unsuccessful plan to merge the University of Chicago and Northwestern University into a single university. During his term, the University of Chicago Hospitals (now called the University of Chicago Medical Center) finished construction and enrolled its first medical students. Also, the Committee on Social Thought, an institution distinctive of the university, was created.
```

## Case 13

- Question ID: `56e1ded7cd28a01900c67bd6`
- Question: What is an example of an NP-intermediate problem not known to exist in P or NP-complete? 
- Saved final passages: 8
- Chunk identifiers stored: yes
- First-retrieval passage text: not stored. No row below uses it.

### Claim 1

```text
The graph isomorphism problem is an example of an NP-intermediate problem not known to exist in P or NP-complete.
```

Stored aggregate result from `squad_cond_C.jsonl` `claim_results`:

- Verdict `CONTRADICTED`; entailment 0.010649; contradiction 0.994770; uncertain `False`.
- Neutral probability: not stored. Per-premise probabilities: not stored. The premise that supplied each maximum: not stored.

Recomputed aggregate on these saved final passages, using `ClaimVerifier._premises` in joint mode and `ClaimVerifier._verdict` at 0.50. This recomputation is part of this diagnostic. It is not a new experiment result.

- Verdict `CONTRADICTED`; entailment 0.010649; contradiction 0.994770; confidence 0.994770.
- Maximum entailment is premise index 4 (Passage 4).
- Maximum contradiction is premise index 6 (Passage 6).
- Those two maxima come from different premises: yes.
- Recomputed aggregate matches the stored verdict and both scores within 1e-6: yes.

Pair-level rows use one saved final passage as the premise and this claim as the hypothesis. The verdict column applies the same 0.50 rule to that pair alone. It is not the verdict stored by Condition C.

| Passage | Chunk ID | Entailment | Contradiction | Neutral | Pair verdict | Differs from stored aggregate? | Role in recomputed aggregate |
|---|---|---:|---:|---:|---|---|---|
| P1 | `computational_complexity_theory-8d3a20bf::c0` | 0.001352 | 0.000765 | 0.997883 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P2 | `computational_complexity_theory-dda0f8e3::c0` | 0.000218 | 0.003068 | 0.996713 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P3 | `computational_complexity_theory-bddbcb45::c0` | 0.000548 | 0.963401 | 0.036051 | `CONTRADICTED` | No |  |
| P4 | `computational_complexity_theory-bac7e499::c0` | 0.010649 | 0.018702 | 0.970648 | `INSUFFICIENT_EVIDENCE` | Yes | max entailment in the joint premise list |
| P5 | `prime_number-33aa9f3d::c0` | 0.000194 | 0.001909 | 0.997898 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P6 | `computational_complexity_theory-98b27f31::c0` | 0.000129 | 0.994770 | 0.005101 | `CONTRADICTED` | No | max contradiction in the joint premise list |
| P7 | `computational_complexity_theory-be6ebefd::c0` | 0.003439 | 0.030596 | 0.965965 | `INSUFFICIENT_EVIDENCE` | Yes |  |
| P8 | `computational_complexity_theory-fb5eb61c::c0` | 0.001376 | 0.875076 | 0.123547 | `CONTRADICTED` | No |  |

Verifier-constructed joint premise, not a retrieved passage: first 320 words of the saved final passages joined in order, capped at 320 words. Pair verdict on this constructed premise alone: `INSUFFICIENT_EVIDENCE` (entailment 0.002746, contradiction 0.002991, neutral 0.994263). This pair verdict differs from the stored aggregate: yes.

```text
Computational_complexity_theory: It was shown by Ladner that if P ≠ NP then there exist problems in NP that are neither in P nor NP-complete. Such problems are called NP-intermediate problems. The graph isomorphism problem, the discrete logarithm problem and the integer factorization problem are examples of problems believed to be NP-intermediate. They are some of the very few NP problems not known to be in P or to be NP-complete. Computational_complexity_theory: The question of whether P equals NP is one of the most important open questions in theoretical computer science because of the wide implications of a solution. If the answer is yes, many important problems can be shown to have more efficient solutions. These include various types of integer programming problems in operations research, many problems in logistics, protein structure prediction in biology, and the ability to find formal proofs of pure mathematics theorems. The P versus NP problem is one of the Millennium Prize Problems proposed by the Clay Mathematics Institute. There is a US$1,000,000 prize for resolving the problem. Computational_complexity_theory: In 1967, Manuel Blum developed an axiomatic complexity theory based on his axioms and proved an important result, the so-called, speed-up theorem. The field really began to flourish in 1971 when the US researcher Stephen Cook and, working independently, Leonid Levin in the USSR, proved that there exist practically relevant problems that are NP-complete. In 1972, Richard Karp took this idea a leap forward with his landmark paper, "Reducibility Among Combinatorial Problems", in which he showed that 21 diverse combinatorial and graph theoretical problems, each infamous for its computational intractability, are NP-complete. Computational_complexity_theory: The graph isomorphism problem is the computational problem of determining whether two finite graphs are isomorphic. An important unsolved problem in complexity theory is whether the graph isomorphism problem is in P, NP-complete, or NP-intermediate. The answer is not known, but it is believed that the problem is at least not NP-complete. If graph
```

### Exact saved final passages

These strings are the Condition C `contexts` field. Passage numbers match the table above.

#### Passage 1

- Chunk ID: `computational_complexity_theory-8d3a20bf::c0`

```text
Computational_complexity_theory: It was shown by Ladner that if P ≠ NP then there exist problems in NP that are neither in P nor NP-complete. Such problems are called NP-intermediate problems. The graph isomorphism problem, the discrete logarithm problem and the integer factorization problem are examples of problems believed to be NP-intermediate. They are some of the very few NP problems not known to be in P or to be NP-complete.
```

#### Passage 2

- Chunk ID: `computational_complexity_theory-dda0f8e3::c0`

```text
Computational_complexity_theory: The question of whether P equals NP is one of the most important open questions in theoretical computer science because of the wide implications of a solution. If the answer is yes, many important problems can be shown to have more efficient solutions. These include various types of integer programming problems in operations research, many problems in logistics, protein structure prediction in biology, and the ability to find formal proofs of pure mathematics theorems. The P versus NP problem is one of the Millennium Prize Problems proposed by the Clay Mathematics Institute. There is a US$1,000,000 prize for resolving the problem.
```

#### Passage 3

- Chunk ID: `computational_complexity_theory-bddbcb45::c0`

```text
Computational_complexity_theory: In 1967, Manuel Blum developed an axiomatic complexity theory based on his axioms and proved an important result, the so-called, speed-up theorem. The field really began to flourish in 1971 when the US researcher Stephen Cook and, working independently, Leonid Levin in the USSR, proved that there exist practically relevant problems that are NP-complete. In 1972, Richard Karp took this idea a leap forward with his landmark paper, "Reducibility Among Combinatorial Problems", in which he showed that 21 diverse combinatorial and graph theoretical problems, each infamous for its computational intractability, are NP-complete.
```

#### Passage 4

- Chunk ID: `computational_complexity_theory-bac7e499::c0`

```text
Computational_complexity_theory: The graph isomorphism problem is the computational problem of determining whether two finite graphs are isomorphic. An important unsolved problem in complexity theory is whether the graph isomorphism problem is in P, NP-complete, or NP-intermediate. The answer is not known, but it is believed that the problem is at least not NP-complete. If graph isomorphism is NP-complete, the polynomial time hierarchy collapses to its second level. Since it is widely believed that the polynomial hierarchy does not collapse to any finite level, it is believed that graph isomorphism is not NP-complete. The best algorithm for this problem, due to Laszlo Babai and Eugene Luks has run time 2O(√(n log(n))) for graphs with n vertices.
```

#### Passage 5

- Chunk ID: `prime_number-33aa9f3d::c0`

```text
Prime_number: A particularly simple example of a probabilistic test is the Fermat primality test, which relies on the fact (Fermat's little theorem) that np≡n (mod p) for any n if p is a prime number. If we have a number b that we want to test for primality, then we work out nb (mod b) for a random value of n as our test. A flaw with this test is that there are some composite numbers (the Carmichael numbers) that satisfy the Fermat identity even though they are not prime, so the test has no way of distinguishing between prime numbers and Carmichael numbers. Carmichael numbers are substantially rarer than prime numbers, though, so this test can be useful for practical purposes. More powerful extensions of the Fermat primality test, such as the Baillie-PSW, Miller-Rabin, and Solovay-Strassen tests, are guaranteed to fail at least some of the time when applied to a composite number.
```

#### Passage 6

- Chunk ID: `computational_complexity_theory-98b27f31::c0`

```text
Computational_complexity_theory: Other important complexity classes include BPP, ZPP and RP, which are defined using probabilistic Turing machines; AC and NC, which are defined using Boolean circuits; and BQP and QMA, which are defined using quantum Turing machines. #P is an important complexity class of counting problems (not decision problems). Classes like IP and AM are defined using Interactive proof systems. ALL is the class of all decision problems.
```

#### Passage 7

- Chunk ID: `computational_complexity_theory-be6ebefd::c0`

```text
Computational_complexity_theory: To further highlight the difference between a problem and an instance, consider the following instance of the decision version of the traveling salesman problem: Is there a route of at most 2000 kilometres passing through all of Germany's 15 largest cities? The quantitative answer to this particular problem instance is of little use for solving other instances of the problem, such as asking for a round trip through all sites in Milan whose total length is at most 10 km. For this reason, complexity theory addresses computational problems and not particular problem instances.
```

#### Passage 8

- Chunk ID: `computational_complexity_theory-fb5eb61c::c0`

```text
Computational_complexity_theory: Upper and lower bounds are usually stated using the big O notation, which hides constant factors and smaller terms. This makes the bounds independent of the specific details of the computational model used. For instance, if T(n) = 7n2 + 15n + 40, in big O notation one would write T(n) = O(n2).
```
