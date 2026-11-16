# Executed release checks

Checks were performed on 2026-11-16 against the extracted release. The code baseline is `c1f1a38a330c77e9b96c344bce3da125ba03873b`. Additional table inputs were projected from the supplied 2026-11-13 manuscript source archive.

| Entry point or check | Executed scope |
| --- | --- |
| `verify.py --output derived` | PASS with 66,027 checks, including 96 release-file SHA-256 checks, saved IDF8 evidence, exact paired significance calculations, MuSiQue partition and nine-schedule numeric reaggregation |
| `scripts/verify_paper_tables.py --output derived_tables` | 309 checks and 12 CSV outputs for saved table values, including paired numeric records for Table 7A and Table 8 |
| `figures/plot_paper_figures.py --output derived_figures` | 3,700 plotted values and three single-page vector PDFs with PNG previews |
| Figure rerun from a separate working directory | Byte-identical generated PDFs, previews, plotted data and report |
| Figure and table input alteration in temporary copies | Rejected by their input-hash checks |
| `pipeline/musique_nine_schedule/selfcheck_control_flow.py` | Synthetic control-flow, stopping, repeat-query and budget checks |
| `pipeline/frozen_reader_conditions/reader_code/score_selfcheck.py` | 69 assertions using the immutable upstream official scoring scripts obtained in a temporary directory |
| Experiment argument-parser entry points | Retrieval, index construction, reader generation, official scoring and nine-schedule help commands |
| `pipeline/check_inputs.py` with absent external assets | Reports the missing inputs and returns status 2 |
| Python source parsing | All 50 distributed Python files parse successfully |
| Source-to-release provenance | Copied root inputs, selected pipeline source hashes, original frozen modules and figure input projections checked |
| Content scan | No matches for the scanned personal-path, common credential, private-key and private-IP patterns in the distributed files |
| Manifest maintenance | An untracked temporary-file probe is excluded from the release manifest |

The standard-library verifiers were executed with Python 3.9.6. Figure generation and package-dependent scoring checks used Python 3.12.14 with ReportLab 4.4.9, pypdfium2 5.13.0 and Pillow 13.0.0 already present in the verification environment. The plotting dependency file pins these observed versions.

Figure 1 and Figure 2 preserve the original curve values and main layout. All three use portable Times-Roman. Figure 3 replays the saved TeX coordinates through ReportLab, so its font metrics and panel geometry differ from the manuscript PDF.

The executed numerical checks operate on saved records and saved aggregates. Table 4 carries the original bootstrap intervals with their provenance and reports that the intervals were not recomputed. Figure 3 retains the saved eight-decimal coordinate precision. The nine-schedule software self-check uses synthetic data. Fresh scientific retrieval, original-label reconstruction, training, reader generation, complete official rescoring and hardware latency measurements require the external inputs listed in `pipeline/README.md`.
