# Paper figure rendering

This directory renders Figures 1–3 of the 2026-11-13 revised clean manuscript from the released aggregate results and saved plotting coordinates. The input projections retain the source values used by the historical drawing programs.

## Run

Use Python 3.11 or newer with the versions in `requirements.txt`. The pinned Pillow 13.0.0 requires Python 3.11+.

```sh
python3 -m pip install -r figures/requirements.txt
python3 figures/plot_paper_figures.py --output derived/figures
```

The program resolves its inputs relative to its own file. An absolute script path works from any working directory. The run reads local files and uses ReportLab's portable Times-Roman font. Its default PNG scale is 2.5 pixels per PDF point and can be changed with `--scale`.

## Figure correspondence

| Paper figure | Generated PDF and PNG basename | Released input | Retained series |
| --- | --- | --- | --- |
| Figure 1 | `matched_query_fullk` | `inputs/matched_query_contrasts.csv` | S2 minus matched Repeat and matched Repeat minus RRF, on 2Wiki, HotpotQA and MuSiQue, at every K from 1 to 400 |
| Figure 2 | `confirmation_fixed_pool_K1_50` | `inputs/confirmation_curves.csv` | Before, frozen reranking and shared-pool ceiling, for S2 and A/C on the three confirmation cohorts, at every K from 1 to 50 |
| Figure 3 | `reverse_curves` | `inputs/reverse_curves.tex` | Exact-title, exact-strict, WordNet-title and WordNet-strict reversal differences on 2Wiki and HotpotQA, at every K from 1 to 50 |

Figure 1 contains 2,400 paired aggregate differences and retains the strict-valid denominators of 12,376, 7,204 and 2,311. Figure 2 reads 300 aggregate rows, each with 1,000 questions, and renders 900 values including each panel's constant pool ceiling across all 50 cutoffs. Figure 3 parses the 400 eight-decimal coordinate values directly from the unmodified historical TeX source. It preserves that saved precision.

## Verification outputs

Every run writes the three PDFs, three PNG previews, `plotted_data.csv` and `plot_verification.json` into the requested output directory. The plotted-data file contains all 3,700 values with figure, dataset, pool, series and K identifiers.

Before drawing, the program checks the SHA-256 of every distributed input against `SOURCES.json`. It checks complete condition/K grids, paired wins/losses and percentage-point differences for Figure 1, and count/rate consistency, fixed pool ceilings and monotone before/after coverage for Figure 2. For Figure 3 it checks panel titles, legend order, saved coordinate grids and the solid/dashed series correspondence. The report records input, plotted-data, script and PDF hashes and checks that each PDF renders as a single page.

`SOURCES.json` records original repository paths and SHA-256 values, the projected input hashes, extraction rules, figure numbers and changes to the drawing logic. The public root `MANIFEST.json` separately binds the published files for the release.

## Rendering and evidence scope

The first two figures reuse the original ReportLab geometry, axis ranges and curve values. All three figures use portable Times-Roman in place of the historical system-specific fonts. Figure 3 uses ReportLab in place of PGFPlots and preserves the two-panel structure and series values. Font metrics, panel geometry for Figure 3 and raster rendering differ from the paper's original PDF files.

This workflow verifies saved aggregate values and regenerates figures. Fresh retrieval, model training, answer generation and original-label validation belong to the experiment workflows and require their external inputs. The historical confirmation plotter also checked an unpublished host-specific protocol before reading its summary. This renderer checks the published aggregate projection and its recorded source hash. Reproducing that earlier protocol audit requires the original protocol and experiment artifacts.
