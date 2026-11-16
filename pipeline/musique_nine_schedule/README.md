# Table 9 nine-schedule MuSiQue experiment

The 2026-11-13 manuscript reports this historical 2,417-record experiment in Table 9. The original published runner has SHA-256 `6c97c18e54c354a413183c573a5d902e6cbdf64e791dc1a9ae95bbf318d75709`. Its distributed adaptation is recorded separately in `../EXTRACTION_MANIFEST.json`.

The four files in `frozen/` retain their original hashes in `frozen_sources.json`. The input/model hash gates and nine depth schedules remain in the runner. The path-independent CPU experiment can be launched on a suitable configured host.

```sh
python3 pipeline/musique_nine_schedule/selfcheck_control_flow.py
python3 pipeline/musique_nine_schedule/run_multiround.py --help
```

The self-check exercises synthetic software control flow. Scientific saved-result verification is available through the root `verify.py`.

The selected original MuSiQue preparation and index code is in `../musique_extension_snapshot/code/`. Full commands and external-input requirements appear in the parent pipeline README.
