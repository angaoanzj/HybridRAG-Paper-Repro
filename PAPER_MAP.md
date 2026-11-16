# Paper claims, implementations and saved evidence

The reference manuscript is the clean revision dated 2026-11-13. Its active build loads `main_clean.tex` → `main.tex` → `abstract.tex` and `paper.tex`, with nine tables and three figures. Table numbers below follow the compiled labels in that revision.

The manuscript's fixed code link points to `angaoanzj/HybridRAG-SDSIC-Repro` at commit `c1f1a38a330c77e9b96c344bce3da125ba03873b`. This repository extracts paper-related implementations and numeric evidence from that public revision and the dated manuscript source package. The original fixed link remains the historical reference. [Paper-cited source revision](https://github.com/angaoanzj/HybridRAG-SDSIC-Repro/tree/c1f1a38a330c77e9b96c344bce3da125ba03873b)

The source revision's pipeline README calls the nine-schedule MuSiQue experiment Table 8. The 2026-11-13 manuscript assigns Table 8 to reversed-order reader scores and Table 9 to the nine-schedule experiment. The earlier saved-result distribution is commit `35eb8899ac8e735a4522c63e4c725d015a68973a`.

## Verification commands

```sh
python3 verify.py --output derived
python3 scripts/verify_paper_tables.py --output derived_tables
python3 figures/plot_paper_figures.py --output derived_figures
```

`verify.py` checks projected question-level records, paired statistical inputs, sample-role lists and the MuSiQue nine-schedule records. `scripts/verify_paper_tables.py` checks additional table cells against saved counts and numeric paired scores. It writes twelve CSV files and `verification.json`. The figure command checks plotting inputs and renders the three figures. Its dependencies are listed in `figures/requirements.txt`.

The checks support the following evidence levels.

- **Saved-record recomputation** aggregates distributed question IDs and numeric per-question outcomes.
- **Saved-aggregate calculation** recomputes rates, differences and accounting identities from historical counts. Previously saved medians and bootstrap bounds retain their original provenance.
- **Saved-aggregate figure rendering** regenerates plots from recorded numeric curves. Figure 3 replays the published TeX coordinates.
- **Implementation reconstruction with external inputs** uses selected original experiment modules together with the matching corpus, labels, protocols, model and index artifacts. Fresh execution remains pending for this extraction.

## Tables 1–5

All paths in the input column are relative to `data/paper_tables/` unless a `data/` prefix is shown. The table-checking entry point is `scripts/verify_paper_tables.py`.

| Paper location and claim | Numeric inputs | Parameters and sample | Derived output | Verification level and remaining inputs |
|---|---|---|---|---|
| Table 1A, `compact_query_table.tex`, matched query replacement and candidate medians | `primary_counts.csv`, `query_unique_medians.csv` | Strict-valid 2Wiki/HotpotQA/MuSiQue cohorts of 12,376/7,204/2,311 questions. S2 and Repeat-q0 share the trigger mask and return/call plan. K=5 and 50 | `derived_tables/table1A.csv` | Saved-aggregate counts and rates. Candidate medians and work-matching flags are checked against their saved summaries. Per-question candidate sets and the exact primary K-range orchestration remain external |
| Table 1B, historical HotpotQA title-level losses | `question_type_counts.csv` | N=7,205, S2 versus original RRF, K=5. Saved loss counts distinguish complete final pools and complete shared initial Top5 | `derived_tables/table1B.csv` | Saved-aggregate arithmetic checks 1,303 losses, 635 wins and 1,293 complete initial Top5 cases. Original title labels, ranked document sets and individual cases remain external |
| Table 2, `review_feedback_table.tex`, IDF contrasts | `data/idf_f2_records.jsonl.gz`, `data/idf_expected.json` | K=2. IDF8 uses three passages, the first 180 words and at most eight terms. Strict-valid cohorts match Table 1A | `derived/idf_feedback.csv`, `derived/verification.json` from `verify.py` | Saved-record recomputation of strict-valid denominators, complete-support counts and IDF8 differences against S2 and RRF. Supplement triggers can differ between IDF8 and S2 |
| Table 2, RM source-depth contrasts | `primary_counts.csv` | RM8, three versus twenty passages, first 180 words, K=10 and pool completeness | `derived_tables/table2_RM.csv` | Saved-aggregate differences. Original term selection and retrieval returns remain external |
| Table 3A, `review_development_table.tex`, own-pool and common eligibility | `development_pairs.csv`, `common_eligible.csv` | N=300 per corpus, S2 and A candidate pools, K=5. These development cohorts selected the reranking blend | `derived_tables/table3A.csv` | Saved-aggregate contingency identities and eligibility denominators. Original classifiers, per-question ranks and feature scores remain external |
| Table 3B, persistent equality and candidate exhaustion | `development_pairs.csv`, `development_exhaustion.csv` | Same development cohorts over every K=1…400 | `derived_tables/table3B.csv` | Saved-aggregate calculation of first persistent zero-discordance, complete-pool equality and list-exhaustion cutoffs. It also checks the recorded temporary equality and two negative counterexamples |
| Table 4, `table_confirmation.tex`, confirmation and oracle accounting | `confirmation_k5.csv`, `confirmation_oracle_k5.csv` | N=1,000 per corpus and pool, K=5. Blend gamma=0.5 for 2Wiki/HotpotQA and 0.25 for MuSiQue. 2Wiki/HotpotQA use source-screened questions. MuSiQue uses historically exposed, group-isolated refitting | `derived_tables/table4.csv` | Saved-aggregate contingency, pool/capacity/selection accounting and cross-file checks. The 95% bootstrap bounds are carried from the saved analysis. Recomputing those intervals requires original per-question ranks and resampling groups |
| Table 5, `table_question_types.tex`, HotpotQA question-type differences | `question_type_counts.csv` | Historical title coverage, 5,755 bridge and 1,450 comparison questions, Score2 versus original RRF at K=5,10,20,50 | `derived_tables/table5.csv` | Saved-aggregate calculation from historical paired win/loss counts. Per-question type assignments and title-label outcomes remain external. This cohort has 7,205 questions |

The selected retrieval, expansion and training primitives are under `pipeline/confirmation/original_code/`. Confirmation entry points are `pipeline/confirmation/scripts/run_confirmation.py` and `verify_and_summarize.py`. Full reconstruction of Table 4 also uses the original frozen selection, source-audit manifests, training-supervision shards and model artifacts. Their expected layout and configurable paths are described in `pipeline/README.md`.

The original primary K-range orchestrator depends on an external `core` module and additional frozen components whose complete identity is unavailable in the cited package. The distributed numeric inputs preserve the recorded primary results. Re-executing that exact historical orchestration remains pending.

## Tables 6–9

| Paper location and claim | Numeric inputs | Parameters and sample | Derived output | Verification level and remaining inputs |
|---|---|---|---|---|
| Table 6A, `table_reader.tex`, coverage and absolute answer scores | `reader_answers_k50.csv`, `reader_coverage_k50.csv`, `reader_air_k50.csv` | Historical N=300 per corpus for 2Wiki and HotpotQA, K=50, eight selected conditions plus AIR | `derived_tables/table6A.csv` | Saved-aggregate rates and rounded official EM/F1 scores. Original questions, answer labels, predictions and canonical reader inputs remain external |
| Table 6B, retained EM differences and paired tests | `data/statistics_inputs.json` | Six contrasts × four cutoffs × two corpora, N=300. Each cutoff is K=10,20,30 or 50 | `derived_tables/table6B.csv` and the `statistics` section of `derived/verification.json` | The table checker calculates all 48 EM differences from paired discordance counts. Root `verify.py` recomputes exact conditional McNemar tests and the recorded adjustment scopes. The retained answer tests use the historical Bonferroni multiplier of 56 |
| Table 7A, `seven_controls_table.tex`, source-family switch | `family_pairs_k50.csv` | 600 numeric paired records, N=300 per corpus, K=50. FewRel-cue Score2 versus Family. Calls, returns, first title and selected-title count are controlled | `derived_tables/table7A.csv` | Saved-record recomputation of changed queries, complete pools, title-complete outputs and paired EM wins/losses. Query text, title strings and answer predictions remain external |
| Table 7B, single-version corpus sensitivity | `dedup_counts_k50.csv` | Separate historical manual-cue cohorts of N=300 per corpus, K=50, dense weights 0.3/0.7. One lexicographically selected document ID per exact title | `derived_tables/table7B.csv` | Saved-aggregate corpus sizes, unreachable-support counts, strict-support counts and Score2–Score1 gaps. Original corpus versions, support labels and the complete sensitivity execution inputs remain external |
| Table 8, `seven_reverse_reader_table.tex`, reversed-order answer scores | `reverse_reader_pairs.csv` | 4,800 numeric paired records covering two corpora, exact/WordNet cue treatments, N=300 per cell and K=10,20,30,50 | `derived_tables/table8.csv` | Saved-record recomputation of EM/F1 macro averages and K=50 paired EM wins/losses. These post hoc comparisons retain their separate statistical scope. Official answer rescoring requires original predictions and labels |
| Table 9, `table_multiround.tex`, nine MuSiQue depth schedules | `data/multiround_quality.jsonl.gz`, `data/multiround_protocol.json`, `data/multiround_expected.json` | 2,417 original development records × nine schedules, K=10,20,30,50, alpha=0.5, CPU8 and a 400-return ceiling | `derived/multiround_table.csv` and the `multiround` section of `derived/verification.json` from `verify.py` | Saved-record recomputation of 21,753 question-condition records, nine schedules, realized calls/returns and eight paired contrasts. Optional original-return replay checks the saved rankings when the matching external archive is supplied |

Historical reader generation uses `pipeline/frozen_reader_conditions/reader_code/generate_answers.py`. Official scoring is orchestrated by `score_all_reader.py`. The immutable upstream scorer locations and hashes are recorded in `pipeline/frozen_reader_conditions/official_scoring_source_receipt.json`. Prompt construction and canonical input preparation are retained under `reader_reference/`. The retrieval conditions are implemented under `retrieval_code/`.

The reader protocol uses `Gemma-4-E4B-it-qat-w4a16-ct` at revision `6cd26aaa`, greedy decoding without thinking and at most 64 output tokens. Documents allow 32 title tokens and 192 body tokens, with a 24,512-token input cap. Fresh generation and official rescoring require the matching checkpoint, tokenizer, canonical inputs, labels and upstream scorer files.

Table 9's original retrieval runner is `pipeline/musique_nine_schedule/run_multiround.py`. Its four frozen retrieval/expansion modules and source-hash receipts accompany it. The extracted runner records path-related adaptations separately in `pipeline/EXTRACTION_MANIFEST.json`. Original MuSiQue input preparation is `pipeline/musique_extension_snapshot/code/prepare_musique.py`.

The MuSiQue roles are preserved separately. The historical nine-schedule study includes all 2,417 records. The primary split removes six normalized duplicates, then assigns 100 calibration/timing IDs and 2,311 effectiveness IDs. The confirmation cohort contains 1,000 separately scoped questions. Root `verify.py` checks the distributed role lists and order-sensitive hashes.

## Figures 1–3

All figure inputs are under `figures/inputs/`. All three use `figures/plot_paper_figures.py`.

| Figure and manuscript source | Input and conditions | Generated files | Verification level |
|---|---|---|---|
| Figure 1, `paper.tex`, `fig_compact_query` | `matched_query_contrasts.csv`, three strict-valid cohorts, S2–Repeat-q0 and Repeat-q0–RRF at all K=1…400. The input has 2,400 rows | `derived_figures/matched_query_fullk.pdf` and `.png` | Saved-aggregate figure rendering with input hashes and complete K-grid checks |
| Figure 2, `paper.tex`, `fig_compact_confirmation` | `confirmation_curves.csv`, N=1,000 per corpus, S2 and A/C fixed pools, K=1…50. The input has 300 rows with saved counts and rates | `derived_figures/confirmation_fixed_pool_K1_50.pdf` and `.png` | Saved-aggregate figure rendering with count/rate checks. The original MuSiQue A/C net loss of one question at K=39 is preserved |
| Figure 3, `paper.tex`, `fig_reverse_fullk` | `reverse_curves.tex`, exact and WordNet title-order contrasts, N=300 per corpus, K=1…50. Eight curves contain 400 coordinates | `derived_figures/reverse_curves.pdf` and `.png` | Original TeX-coordinate replay and rendering. Recovering the underlying per-question coverage thresholds requires additional historical records |

The figure command additionally writes `plotted_data.csv` and `plot_verification.json`. The portable renderer uses a locally available serif font and records its rendering setup. Layout and font rendering can differ from the historical TeX and platform-specific figure builds while the saved numeric plotting values remain bound by hashes.

## Input provenance and reconstruction limits

`data/paper_tables/SOURCES.json` records the dated source archive hash, each original project-relative member name and hash, the distributed hash, row count and projection policy. The table inputs contain numeric aggregates or question IDs with Boolean/numeric outcomes. `figures/SOURCES.json` records the plotting projections. `pipeline/EXTRACTION_MANIFEST.json` records selected source files and adaptations.

The table checker verifies saved numerical evidence against the manuscript's displayed values. The original raw labels and retrieval calls remain the source of scientific validity. The Table 4 confidence bounds retain the original descriptive bootstrap calculation, including its fixed model and split. The Table 1 medians retain their saved aggregate calculation. The Table 6A and Table 7B inputs retain their historical scoring and corpus-audit aggregates.

Fresh retrieval, training, answer generation, complete label reconstruction and timing measurements require the external scientific inputs and a recorded runtime. Running the saved-result commands establishes the distributed numeric checks and plotting chain described above.
