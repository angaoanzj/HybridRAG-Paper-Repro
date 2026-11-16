"""List missing external experiment inputs without importing model libraries."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='experiment', required=True)
    confirmation = commands.add_parser('confirmation', help='Frozen three-corpus confirmation inputs')
    confirmation.add_argument('--root', type=Path, required=True)
    confirmation.add_argument('--original-training-root', type=Path, required=True)
    confirmation.add_argument('--data-root', type=Path, required=True)
    confirmation.add_argument('--model', type=Path, required=True)
    musique = commands.add_parser('musique', help='Historical Table 9 input files')
    musique.add_argument('--study-root', type=Path, required=True)
    musique.add_argument('--model', type=Path, required=True)
    reader = commands.add_parser('reader', help='Frozen 19-condition reader inputs')
    reader.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    required = []
    missing_patterns = []
    mismatches = []
    if args.experiment == 'confirmation':
        required += [args.root / 'frozen' / name for name in (
            'protocol.json', 'protocol.sha256', 'musique_ids.json',
            'musique_selected_groups.json', '2wiki_questions.json', 'hotpotqa_questions.json')]
        required.append(args.original_training_root / 'protocol.json')
        protocol_path = args.root / 'frozen/protocol.json'
        if protocol_path.is_file():
            protocol = json.loads(protocol_path.read_text())
            required += [args.root / 'frozen' / name for name in protocol.get('frozen_files', {})]
        for dataset in ('2wiki', 'hotpotqa', 'musique'):
            required += [args.data_root / 'data' / dataset / name for name in ('corpus.jsonl', 'questions.json')]
            required += [args.data_root / 'indexes' / dataset / name for name in ('index_manifest.json', 'embeddings.npy')]
            required += [args.original_training_root / 'models' / dataset / name for name in ('document_ranker.joblib', 'frozen.json')]
        if not list((args.original_training_root / 'supervision/musique').glob('train_*.npz')):
            missing_patterns.append(str(args.original_training_root / 'supervision/musique/train_*.npz'))
        required += [args.model / name for name in ('config.json', 'tokenizer.json')]
        required += [path.with_suffix('.json') for path in (args.original_training_root / 'supervision/musique').glob('train_*.npz')]
        if not any(path.is_file() and path.suffix in ('.safetensors', '.bin') for path in args.model.rglob('*')):
            missing_patterns.append(str(args.model / '*.safetensors or *.bin'))
    elif args.experiment == 'musique':
        required += [args.study_root / 'data/musique' / name for name in ('public.json', 'labels.json', 'corpus.jsonl')]
        required += [args.study_root / 'indexes/musique' / name for name in ('index_manifest.json', 'embeddings.npy', 'docids.json', 'sparse_bm25.npz', 'sparse_metadata.json', 'vocabulary.json')]
        expected = json.loads((Path(__file__).parent / 'musique_nine_schedule/original_data_manifest.json').read_text())
        for name, key in (('public.json', 'public_sha256'), ('labels.json', 'labels_sha256'), ('corpus.jsonl', 'corpus_sha256')):
            path = args.study_root / 'data/musique' / name
            if path.is_file() and digest(path) != expected[key]:
                mismatches.append(str(path))
        manifest_path = args.study_root / 'indexes/musique/index_manifest.json'
        if manifest_path.is_file():
            manifest = json.loads(manifest_path.read_text())
            for relative, record in manifest.get('model_files', {}).items():
                path = args.model / relative
                required.append(path)
                if path.is_file() and digest(path) != record['sha256']:
                    mismatches.append(str(path))
        elif not args.model.is_dir():
            missing_patterns.append(str(args.model))
    else:
        required += [args.root / name for name in (
            'inputs/input_preparation_receipt.json', 'inputs/reader_config.json',
            'inputs/unique_inputs.jsonl.gz', 'inputs/group_input_map.jsonl.gz', 'inputs/history_selected_predictions.jsonl.gz',
            'retrieval_protocol.json', 'receipts/service_before.json')]
        receipt_path = args.root / 'inputs/input_preparation_receipt.json'
        if receipt_path.is_file():
            receipt = json.loads(receipt_path.read_text())
            required += [args.root / 'inputs' / name for name in receipt.get('files', {})]
    missing = [str(path) for path in required if not path.is_file()] + missing_patterns
    status = 'INPUT_FILES_PRESENT_RUNTIME_UNVERIFIED' if not missing and not mismatches else 'EXTERNAL_INPUTS_INCOMPLETE'
    print(json.dumps({'status': status, 'experiment': args.experiment,
                      'required_file_checks': len(required), 'missing': missing,
                      'hash_mismatches': mismatches, 'retrieval_or_inference_executed': False}, indent=2))
    return 0 if not missing and not mismatches else 2


if __name__ == '__main__':
    raise SystemExit(main())
