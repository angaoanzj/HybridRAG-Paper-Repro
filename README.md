# HybridRAG paper reproduction code

This repository extracts the implementation and numeric inputs associated with the **2026-11-13 clean manuscript revision** of the HybridRAG case study. Its source baseline is commit `c1f1a38a330c77e9b96c344bce3da125ba03873b` of `angaoanzj/HybridRAG-SDSIC-Repro`, the revision cited by the manuscript.

Additional numeric table projections come from `HybridRAG_LaTeX修订源码_20261113.zip` in the manuscript delivery package. `data/paper_tables/SOURCES.json` records the archive hash, source-file hashes and projection rules.

The release contains a portable saved-result verifier, the generation chain for the three manuscript figures, and selected experiment implementations with their external-input requirements. [PAPER_MAP.md](PAPER_MAP.md) maps the nine tables and three figures to their available code and inputs.

## Verify saved results

Use Python 3.9 or newer. This entry point uses the Python standard library.

```sh
python3 verify.py --output derived
```

The command checks every file listed in `MANIFEST.json`, recomputes the IDF8 comparison at K=2, repeats the saved paired significance calculations, checks the MuSiQue sample partition, and reconstructs the historical nine-schedule result table from projected per-question numeric records. Successful execution prints `PASS` and writes `verification.json`, `idf_feedback.csv`, and `multiround_table.csv`.

The nine-schedule study is **Table 9 in the 2026-11-13 manuscript**. The upstream snapshot described it as Table 8. Its historical cohort has 2,417 original records and includes the duplicate and calibration records that were excluded from the primary 2,311-question effectiveness cohort. The measured multi-round cutoffs are K=10,20,30,50.

## Recompute the other saved table values

```sh
python3 scripts/verify_paper_tables.py --output derived_tables
```

This standard-library entry point reconstructs the available table values from projected numeric records and saved aggregate counts. It writes 12 CSV outputs covering Tables 1–8, with the IDF contrasts and retained reader significance tests handled by the root verifier. Table 7A and Table 8 use paired per-question numeric records. The remaining inputs preserve their aggregate evidence level.

Table 4's historical bootstrap bounds are carried with their provenance. This command checks the associated saved counts and reports `bootstrap_intervals_recomputed=false`. The table and figure mappings identify each cohort and denominator.

## Recreate manuscript figures

Use Python 3.11 or newer with the pinned plotting dependencies.

```sh
python3 -m pip install -r figures/requirements.txt
python3 figures/plot_paper_figures.py --output derived_figures
```

The figure program uses the saved aggregate inputs included in this release. It regenerates the plotted data for Figures 1–3. Rendering and font adaptations are documented in [figures/README.md](figures/README.md).

## Reconstruct experiments with external inputs

[pipeline/README.md](pipeline/README.md) describes the selected retrieval, title expansion, fixed-pool reranking, reader, and MuSiQue nine-schedule implementations. It lists the required datasets, frozen models, indexes, protocols, and commands for each retained entry point. Use a dedicated environment for these experiment dependencies.

```sh
python3 -m pip install -r requirements-experiments.txt
```

Full experiment reconstruction depends on matching external inputs and the original experimental protocol. The validation performed for this extraction covers the runnable checks described below. Model training, fresh corpus retrieval, reader generation, and latency measurements require their own execution and validation.

## Optional saved-return replay and source-data sampling

The original verifier also accepts the original raw-return archive and the official MuSiQue source data.

```sh
python3 verify.py --raw-returns /path/to/raw_rankings_and_calls.jsonl.gz --output derived_raw
python3 verify.py --musique-data /path/to/musique_data_v1.0.zip --output derived_sampling
```

The raw-return option checks the expected archive hash and replays the saved weighted reciprocal-rank fusion trajectories. The MuSiQue option repeats normalization and first-occurrence deduplication from the official question text. Obtain these external inputs under their upstream terms. The original raw-return archive has SHA-256 `f3b2ab45895d4039f3c2141583b2c2ed2e2f664f04e460060539180921e89552`.

FT is reaggregated from saved numeric quality records. Original title-label reconstruction requires the corresponding original labels. Evidence-coverage calculations and reader-answer measurements have separate inputs and validation scopes in `PAPER_MAP.md`.

## Provenance and validation

`ORIGIN.json` records the source commit and the hashes of the copied verifier inputs. The pipeline and figure directories carry their own source-to-distribution mappings. `MANIFEST.json` binds the files in this extracted release by SHA-256. After selecting and staging release-file changes with Git, regenerate the manifest with the included maintenance command, then stage `MANIFEST.json` before committing.

```sh
python3 scripts/update_manifest.py
python3 verify.py --output derived
```

The original baseline passed a fresh-clone verification with **66,047 checks**, including 116 manifest entries, on 2026-11-16. The extracted release has its own manifest and check count. The count changes with the number of distributed files. The current extraction's executed checks are recorded in [VALIDATION.md](VALIDATION.md).

## Data and software terms

Numeric projections and source references are supplied with their recorded provenance. Datasets, model weights, indexes, and upstream evaluation software must be obtained under their respective terms. This extraction preserves upstream attribution and carries no additional software or dataset license grant.
