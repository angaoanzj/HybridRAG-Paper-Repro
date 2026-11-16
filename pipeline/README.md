# Paper experiment implementations

These files are selected from the paper-cited revision `c1f1a38a330c77e9b96c344bce3da125ba03873b`. The manuscript dated 2026-11-13 has nine tables and three figures. Its historical nine-schedule MuSiQue study is Table 9.

The root `verify.py` entry point recomputes the distributed saved results. The implementations below support reconstruction when the matching external corpora, frozen protocols, sample lists, models and indexes are supplied. Fresh retrieval, training and reader inference remain unexecuted for this extraction.

## Selected implementations

| Directory | Paper connection | Runtime inputs |
|---|---|---|
| `confirmation/original_code/` | Title expansion, public-text feedback, fixed-pool features, ranker training and retrieval primitives used in the confirmation experiment | Prepared corpora, labels, indexes, BGE checkpoint and training protocol |
| `confirmation/scripts/` | Table 4 and Figure 2 confirmation selection, original training-row exclusion, retraining, paired ranking verification and aggregation | Original frozen confirmation bundle, source-audited candidate manifests, original training supervision and frozen rankers |
| `frozen_reader_conditions/retrieval_code/` | Fixed-index title-selection, vocabulary, family and reversal conditions for Tables 6–8 and Figure 3 | Original public question lists, fixed corpus/index, frozen retrieval protocol, cue configuration and WordNet files |
| `frozen_reader_conditions/reader_reference/` | Original prompt construction and canonical input reconstruction | Saved retrieval contexts, tokenizer/checkpoint, reader service and historical prediction bundles |
| `frozen_reader_conditions/reader_code/` | Frozen reader generation, official answer scoring and paired statistics | Canonical reader inputs, frozen generation plan, original labels and pinned official evaluation scripts |
| `musique_extension_snapshot/code/` | Exact MuSiQue corpus preparation, original index construction and hop-level paragraph scoring | Official MuSiQue-Ans v1.0 development file and matching BGE checkpoint |
| `musique_nine_schedule/` | Table 9 nine-schedule experiment and its deterministic software checks | Prepared original 2,417-question study, index, matching model and original hash manifests |

`EXTRACTION_MANIFEST.json` records each retained source path, original published SHA-256, distributed SHA-256 and adaptation. `SOURCE_MANIFEST.json` also preserves the earlier source-versus-publication history for Python files. Paths were made configurable. Query selection, ranker parameters, budget settings, scoring definitions, sample roles and original input hash gates retain their recorded values.

The old K-range orchestration imports an external `core` module and frozen dependencies whose complete identity is unavailable in the source package. Its archived entry points are outside this extracted implementation set. The selected K-range aggregate inputs support saved-result and figure reconstruction described by the root README.

## Environment

Use Python 3.10 or newer for the experiment implementations. The root saved-result verifier separately supports Python 3.9 or newer.

```sh
python3 -m pip install -r requirements-experiments.txt
python3 pipeline/check_inputs.py --help
python3 pipeline/musique_nine_schedule/selfcheck_control_flow.py
```

The dependency file lists imported packages. Exact original package versions remain unavailable. GPU training and original index construction require a compatible PyTorch/CUDA environment. The reader client uses a local OpenAI-compatible service. Reconstructing the archived reader service also requires its original vLLM, compressed-tensors and checkpoint combination.

The nine-schedule self-check uses synthetic records and exercises budgets, stopping, repeated queries and matching prefixes. It supplies a software check only. Root `verify.py` supplies the saved scientific-result check.

## Frozen three-corpus confirmation

The retained source supports the same three-corpus confirmation process when its frozen artifacts are provided. A preliminary file check can run without scientific Python or model imports.

```sh
python3 pipeline/check_inputs.py confirmation \
  --root external/confirmation \
  --original-training-root external/original_training \
  --data-root external/prepared_data \
  --model external/models/bge
```

The confirmation root must contain `frozen/protocol.json`, `protocol.sha256`, every file bound by `protocol.frozen_files`, the question selection files and the MuSiQue group/role IDs. The original training root must contain `protocol.json`, frozen rankers and MuSiQue `supervision/train_*.npz` with their paired metadata. The data root must contain `data/<dataset>/corpus.jsonl`, `questions.json` and `indexes/<dataset>/` for `2wiki`, `hotpotqa` and `musique`.

```sh
export HYBRIDRAG_CONFIRMATION_ROOT=external/confirmation
export HYBRIDRAG_ORIGINAL_TRAINING_ROOT=external/original_training
export HYBRIDRAG_DATA_ROOT=external/prepared_data
export HYBRIDRAG_BGE_MODEL=external/models/bge
python3 pipeline/confirmation/scripts/run_confirmation.py
python3 pipeline/confirmation/scripts/verify_and_summarize.py
```

The source-audited question-selection builder is `confirmation/scripts/freeze_confirmation.py`. It requires the original candidate audit manifests under `HYBRIDRAG_SOURCE_AUDIT_ROOT` and original protocol at `HYBRIDRAG_ORIGINAL_PROTOCOL`. These manifests and training shards are external artifacts. Their absence prevents a complete reconstruction from the distributed files alone. Using the recorded frozen selection preserves the original sample identities.

`HYBRIDRAG_TRAINING_ROOT` configures the artifact root used by the retained original training modules. `full_train.py` expects its recorded protocol, supervision files and generated manifests at that root. It is also imported by the confirmation runner for its original sampler and backend definitions.

## Fixed-index title conditions

The retained current runner exposes all experiment inputs explicitly.

```sh
python3 pipeline/frozen_reader_conditions/retrieval_code/reviewer_runner.py --help
python3 pipeline/frozen_reader_conditions/retrieval_code/build_index.py --help
```

The 19-condition vocabulary implementation requires `HYBRIDRAG_CUE_FILE`, `HYBRIDRAG_CUE_SHA256` and `HYBRIDRAG_WORDNET_DIR`. The cue configuration must have its original `mined_without_task_labels` receipt and matching WordNet hashes. The retrieval runner additionally verifies the supplied frozen protocol hash and public-only question schema. The original cue configuration and complete frozen retrieval input bundle remain external.

## Reader generation and official scoring

The current prompt-input exporter uses `HYBRIDRAG_RETRIEVAL_ROOT` for saved retrieval runs and `HYBRIDRAG_READER_EXPORT_ROOT` for its output. The canonical input preparer uses `HYBRIDRAG_READER_ROOT`, `HYBRIDRAG_READER_MODEL` and `HYBRIDRAG_READER_ENDPOINT`, whose default endpoint is `http://127.0.0.1:18271`. Its three archived reuse bundles are configured through `HYBRIDRAG_READER_MATCHED_HISTORY`, `HYBRIDRAG_READER_PILOT_HISTORY` and `HYBRIDRAG_READER_AIR_HISTORY`.

The canonical preparer validates archived protocols against the original published prompt-worker hash stored in `EXTRACTION_MANIFEST.json`. It separately records the distributed, path-configured worker hash. This preserves the original history identity after the path adaptation.

Once canonical inputs and the frozen service receipts are present, use the retained entry points.

```sh
python3 pipeline/check_inputs.py reader --root external/reader
python3 pipeline/frozen_reader_conditions/reader_code/freeze_reader_plan.py --root external/reader
python3 pipeline/frozen_reader_conditions/reader_code/generate_answers.py --root external/reader
python3 pipeline/frozen_reader_conditions/reader_code/score_all_reader.py --help
```

`freeze_reader_plan.py` writes a new plan when the original pre-generation conditions are met. For reconstruction from the original frozen bundle, its archived `analysis_plan.json` provides the existing generation plan. `generate_answers.py` preserves successful predictions and frozen identities on resume.

`official_scoring_source_receipt.json` provides immutable upstream URLs, commits and SHA-256 values for official HotpotQA and 2Wiki scoring scripts. Obtain those files from their upstream repositories under the applicable terms. The canonical answer field and the later answer-ID alias protocol have separate recorded scoring identities.

The preparation and generation workflow depends on the original retrieval protocol, canonical contexts, historical prediction bundles and reader checkpoint. These items remain external. The extracted files support inspecting the exact operations and reconstructing them when those inputs are available.

## MuSiQue preparation and Table 9

Obtain `musique_ans_v1.0_dev.jsonl` from the official MuSiQue distribution. Its required SHA-256 is `15fa63794d18a94ce12411aca6e2327e65b6e83b0b1490efab3f1962e48abf3b`.

```sh
export HYBRIDRAG_MUSIQUE_ROOT=external/musique
export HYBRIDRAG_MUSIQUE_SOURCE=external/downloads/musique_ans_v1.0_dev.jsonl
python3 pipeline/musique_extension_snapshot/code/prepare_musique.py
```

Preparation generates the original public questions, labels and exact-title-plus-paragraph corpus. To build the original index with the matching local BGE checkpoint, call the retained original index function from its module directory.

```sh
export EXTENSION_MODEL=external/models/bge
python3 -c "import sys; sys.path.insert(0, 'pipeline/musique_extension_snapshot/code'); import study; study.index('musique')"
python3 pipeline/check_inputs.py musique \
  --study-root external/musique --model external/models/bge
python3 pipeline/musique_nine_schedule/run_multiround.py \
  --study-root external/musique --model external/models/bge \
  --out derived/musique_nine --preflight-only
python3 pipeline/musique_nine_schedule/run_multiround.py \
  --study-root external/musique --model external/models/bge \
  --out derived/musique_nine --execute
```

The index builder uses the original GPU encoding configuration. The nine-schedule runner performs CPU retrieval and checks the original corpus, public inputs, labels, index/model files and frozen module hashes. The four frozen retrieval modules retain their exact published bytes. The historical AutoDL-specific host gate was removed from the distributed runner. Its actual environment and produced outputs must still be recorded for a fresh execution.

Table 9 uses the original 2,417 development records, including the six normalized duplicates and calibration/timing questions. The primary effectiveness cohort has 2,311 IDs. Keep those recorded roles attached to all derived outputs.

## Validation for this extraction

All retained Python sources pass syntax parsing. The nine-schedule synthetic self-check passes. Official-scoring fixtures pass 69 assertions using the pinned upstream evaluation scripts in a temporary directory, including empty-token F1 and fail-closed input joins. The argument parsers for the retrieval runner, reader generator, official scorer, index builder and nine-schedule runner are exercised. The pure-standard-library input checker reports missing external inputs with a nonzero exit status.

Fresh scientific retrieval, GPU training, reader generation, complete official rescoring and hardware timing require the external inputs and experiment runtime. Their execution remains pending. The root README records the independently executed saved-result and figure checks for this extracted release.
