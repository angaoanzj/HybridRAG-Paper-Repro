#!/usr/bin/env python3
"""Check paper-table values from projected saved counts and numeric paired scores."""
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "paper_tables"
CHECKS = 0


def require(condition, message):
    global CHECKS
    CHECKS += 1
    if not condition:
        raise ValueError(message)


def read_csv(name):
    with (DATA / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def count(row, key):
    return int(row[key])


def rounded(value):
    return round(value, 2)


def compare(rows, fields, expected, name):
    actual = [tuple(row[field] for field in fields) for row in rows]
    require(actual == expected, name + " disagrees with the 2026-11-13 manuscript values")


def verify_hashes():
    manifest = json.loads((DATA / "SOURCES.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        path = ROOT / entry["published_path"]
        require(
            path.resolve().is_relative_to(DATA.resolve()), "Input outside paper-table directory"
        )
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == entry["published_sha256"],
            "Input hash mismatch " + entry["published_path"],
        )
        require(
            len(read_csv(path.name)) == entry["records"], "Input row-count mismatch " + path.name
        )


def query_and_feedback():
    counts = {(r["dataset"], r["method"], count(r, "K")): r for r in read_csv("primary_counts.csv")}
    medians = {r["dataset"]: r for r in read_csv("query_unique_medians.csv")}
    table1 = []
    table2_rm = []
    for dataset in ["2wiki", "hotpotqa", "musique"]:
        for method, policy, median_field in [
            ("repeat_q0_s2mask", "Repeat-q0", "repeat_unique_docs_median"),
            ("no_second_branch", "S2", "S2_unique_docs_median"),
        ]:
            five, fifty = counts[dataset, method, 5], counts[dataset, method, 50]
            n = count(five, "strict_valid_n")
            require(
                n == count(fifty, "strict_valid_n") == count(medians[dataset], "questions"),
                "Query cohort mismatch",
            )
            require(
                medians[dataset]["D_and_calls_equal_all_questions"] == "True",
                "Saved matched-work flag is false",
            )
            table1.append(
                {
                    "dataset": dataset,
                    "policy": policy,
                    "N": n,
                    "pool_complete": count(five, "pool_complete_n"),
                    "F5": count(five, "support_complete_n"),
                    "F50": count(fifty, "support_complete_n"),
                    "median_unique_candidates_saved": float(medians[dataset][median_field]),
                }
            )
        low, high = (
            counts[dataset, "rm_m3_head180_w8", 10],
            counts[dataset, "rm_m20_head180_w8", 10],
        )
        n = count(low, "strict_valid_n")
        require(n == count(high, "strict_valid_n"), "RM cohort mismatch")
        table2_rm.append(
            {
                "dataset": dataset,
                "N": n,
                "K": 10,
                "RM20_minus_RM3_F10_pp": rounded(
                    100 * (count(high, "support_complete_n") - count(low, "support_complete_n")) / n
                ),
                "RM20_minus_RM3_pool_pp": rounded(
                    100 * (count(high, "pool_complete_n") - count(low, "pool_complete_n")) / n
                ),
            }
        )
    compare(
        table1,
        ["N", "pool_complete", "F5", "F50", "median_unique_candidates_saved"],
        [
            (12376, 6852, 4310, 6155, 190.0),
            (12376, 11217, 7307, 10888, 345.0),
            (7204, 6760, 4865, 6395, 182.0),
            (7204, 7031, 4208, 6756, 282.0),
            (2311, 1469, 358, 1082, 180.0),
            (2311, 1706, 365, 1297, 269.0),
        ],
        "Table 1A",
    )
    compare(
        table2_rm,
        ["RM20_minus_RM3_F10_pp", "RM20_minus_RM3_pool_pp"],
        [(-5.48, -1.59), (-9.73, -0.50), (-6.58, -2.08)],
        "Table 2 RM contrasts",
    )
    return {"table1A": table1, "table2_RM": table2_rm}


def question_types():
    records = read_csv("question_type_counts.csv")
    indexed = {(r["type"], count(r, "K")): r for r in records}
    table5 = []
    for k in [5, 10, 20, 50]:
        row = {"K": k}
        for kind in ["bridge", "comparison"]:
            source = indexed[kind, k]
            wins = count(source, "Score2_win_RRF_loss")
            losses = count(source, "RRF_win_Score2_loss")
            require(
                wins - losses == count(source, "Score2_net_questions"),
                "Question-type paired-count mismatch",
            )
            row[kind + "_N"] = count(source, "questions")
            row[kind + "_delta_pp"] = rounded(100 * (wins - losses) / count(source, "questions"))
        require(
            row["bridge_N"] + row["comparison_N"] == count(indexed["ALL", k], "questions") == 7205,
            "Question-type denominator mismatch",
        )
        table5.append(row)
    compare(
        table5,
        ["bridge_delta_pp", "comparison_delta_pp"],
        [(-0.54, -43.93), (1.34, -25.10), (4.52, -7.52), (5.44, -0.14)],
        "Table 5",
    )
    source = indexed["ALL", 5]
    table1b = [
        {
            "N": count(source, "questions"),
            "K": 5,
            "losses": count(source, "RRF_win_Score2_loss"),
            "wins": count(source, "Score2_win_RRF_loss"),
            "losses_complete_pool": count(source, "loss_all_gold_in_final_pool"),
            "losses_complete_initial_top5": count(source, "loss_common_q0_already_complete"),
        }
    ]
    compare(
        table1b,
        ["N", "losses", "wins", "losses_complete_pool", "losses_complete_initial_top5"],
        [(7205, 1303, 635, 1303, 1293)],
        "Table 1B",
    )
    return {"table1B": table1b, "table5": table5}


def development():
    records = read_csv("development_pairs.csv")
    indexed = {(r["dataset"], r["pool_method"], count(r, "K")): r for r in records}
    common = {r["dataset"]: r for r in read_csv("common_eligible.csv")}
    table3a = []
    for dataset in ["2wiki", "hotpotqa", "musique"]:
        c = common[dataset]
        require(
            sum(
                count(c, k)
                for k in ["both_rescued", "only_S2_rescued", "only_A_rescued", "neither_rescued"]
            )
            == count(c, "n"),
            "Common-eligibility partition mismatch",
        )
        for pool in ["S2", "A"]:
            r = indexed[dataset, pool, 5]
            require(
                count(r, "F1") - count(r, "F0") == count(r, "W") - count(r, "L"),
                "Development wins/losses mismatch",
            )
            require(
                count(r, "rescue_denominator") == count(r, "P") - count(r, "F0"),
                "Development rescue denominator mismatch",
            )
            table3a.append(
                {
                    "dataset": dataset,
                    "pool": pool,
                    "N": count(r, "strict_n"),
                    "P": count(r, "P"),
                    "before": count(r, "F0"),
                    "after": count(r, "F1"),
                    "wins": count(r, "W"),
                    "losses": count(r, "L"),
                    "own_eligible": count(r, "rescue_denominator"),
                    "common_rescued": count(c, pool + "_rescued"),
                    "common_eligible": count(c, "n"),
                }
            )
    compare(
        table3a,
        [
            "P",
            "before",
            "after",
            "wins",
            "losses",
            "own_eligible",
            "common_rescued",
            "common_eligible",
        ],
        [
            (265, 124, 188, 76, 12, 141, 59, 116),
            (283, 91, 173, 90, 8, 192, 53, 116),
            (286, 158, 215, 62, 5, 128, 27, 85),
            (295, 178, 214, 45, 9, 117, 29, 85),
            (200, 34, 46, 14, 2, 166, 2, 144),
            (226, 38, 41, 4, 1, 188, 2, 144),
        ],
        "Table 3A",
    )
    exhaustion = read_csv("development_exhaustion.csv")
    table3b = []
    for dataset, pool in [("2wiki", "S2"), ("musique", "A")]:
        series = [indexed[dataset, pool, k] for k in range(1, 401)]
        last_discordance = max(
            count(r, "K") for r in series if count(r, "W") != 0 or count(r, "L") != 0
        )
        last_incomplete = max(
            count(r, "K")
            for r in series
            if count(r, "F0") != count(r, "P") or count(r, "F1") != count(r, "P")
        )
        exhausted = [
            count(r, "K")
            for r in exhaustion
            if r["dataset"] == dataset
            and r["pool_method"] == pool
            and count(r, "exhausted_n") == count(r, "strict_n")
        ]
        table3b.append(
            {
                "dataset": dataset,
                "pool": pool,
                "K_persistent_W_L_zero": last_discordance + 1,
                "K_persistent_F0_F1_P_equal": last_incomplete + 1,
                "K_all_lists_exhausted": min(exhausted),
            }
        )
    compare(
        table3b,
        ["K_persistent_W_L_zero", "K_persistent_F0_F1_P_equal", "K_all_lists_exhausted"],
        [(291, 291, 386), (303, 319, 370)],
        "Table 3B",
    )
    require(
        all(
            count(indexed["2wiki", "S2", k], "W") == count(indexed["2wiki", "S2", k], "L") == 1
            for k in range(192, 204)
        ),
        "Table 3B temporary equality mismatch",
    )
    require(
        (count(indexed["musique", "A", 7], "W"), count(indexed["musique", "A", 7], "L")) == (4, 7),
        "Table 3 MuSiQue counterexample mismatch",
    )
    require(
        (count(indexed["2wiki", "S2", 224], "W"), count(indexed["2wiki", "S2", 224], "L"))
        == (0, 1),
        "Table 3 2Wiki counterexample mismatch",
    )
    return {"table3A": table3a, "table3B": table3b}


def confirmation():
    oracle = {
        (r["dataset"], r["pool"], r["ranking"]): r for r in read_csv("confirmation_oracle_k5.csv")
    }
    table4 = []
    for r in read_csv("confirmation_k5.csv"):
        n, p, before, after, wins, losses = [
            count(r, k) for k in ["n", "pool_complete", "before", "after", "wins", "losses"]
        ]
        require(n == 1000 and after - before == wins - losses, "Confirmation contingency mismatch")
        for ranking, observed in [("before", before), ("after", after)]:
            o = oracle[r["dataset"], r["pool"], ranking]
            require(
                count(o, "oracle_feasible") == p and count(o, "capacity_failure") == 0,
                "Confirmation oracle mismatch",
            )
            require(count(o, "observed_complete") == observed, "Confirmation output count mismatch")
        table4.append(
            {
                "dataset": r["dataset"],
                "pool": r["pool"],
                "N": n,
                "P_equals_U5": p,
                "before": before,
                "after": after,
                "wins": wins,
                "losses": losses,
                "delta_pp": rounded(100 * (after - before) / n),
                "CI95_low_saved_pp": rounded(100 * float(r["delta_ci95_low_saved"])),
                "CI95_high_saved_pp": rounded(100 * float(r["delta_ci95_high_saved"])),
                "pool_misses": n - p,
                "selection_failures_before": p - before,
                "selection_failures_after": p - after,
            }
        )
    compare(
        table4,
        [
            "P_equals_U5",
            "before",
            "after",
            "wins",
            "losses",
            "delta_pp",
            "CI95_low_saved_pp",
            "CI95_high_saved_pp",
        ],
        [
            (803, 343, 607, 276, 12, 26.4, 23.4, 29.3),
            (863, 164, 538, 380, 6, 37.4, 34.6, 40.3),
            (957, 562, 769, 232, 25, 20.7, 18.1, 23.4),
            (977, 654, 773, 136, 17, 11.9, 9.7, 14.1),
            (614, 142, 184, 46, 4, 4.2, 2.62, 6.34),
            (705, 120, 146, 34, 8, 2.6, 1.15, 4.47),
        ],
        "Table 4",
    )
    return {"table4": table4}


def reader_scores():
    answers = {(r["dataset"], r["policy"]): r for r in read_csv("reader_answers_k50.csv")}
    coverage = {(r["dataset"], r["policy"]): r for r in read_csv("reader_coverage_k50.csv")}
    air = {r["dataset"]: r for r in read_csv("reader_air_k50.csv")}
    policies = [
        ("RRF", "hybrid_rrf"),
        ("AIR", None),
        ("Score1", "score1_u24"),
        ("Order2", "first_two_valid_titles"),
        ("Score2", "score2_u24"),
        ("Family", "family_u24"),
        ("Synonyms", "no_second_branch"),
        ("Reversed exact", "reverse_u24"),
        ("Reversed synonyms", "score_two_reverse"),
    ]
    table6 = []
    for label, policy in policies:
        for dataset in ["2wiki", "hotpotqa"]:
            if policy is None:
                r = air[dataset]
                n, ft, em, f1 = (
                    count(r, "n"),
                    count(r, "full_coverage_count"),
                    count(r, "EM_count"),
                    float(r["F1"]),
                )
            else:
                a, c = answers[dataset, policy], coverage[dataset, policy]
                n, ft, em, f1 = (
                    count(a, "n"),
                    count(c, "F_count"),
                    count(a, "EM_count"),
                    float(a["F1_points"]),
                )
                require(n == count(c, "n"), "Reader coverage/answer denominator mismatch")
            require(n == 300, "Reader cohort mismatch")
            table6.append(
                {
                    "policy": label,
                    "dataset": dataset,
                    "N": n,
                    "K": 50,
                    "title_complete_percent": rounded(100 * ft / n),
                    "EM_percent": rounded(100 * em / n),
                    "F1_points": rounded(f1),
                }
            )
    compare(
        table6,
        ["title_complete_percent", "EM_percent", "F1_points"],
        [
            (46, 25.33, 28.18),
            (91, 35.33, 48.98),
            (46.67, 27, 29.02),
            (92, 36.33, 48.57),
            (71.67, 24.67, 26.53),
            (92.33, 38.67, 50.76),
            (83.67, 27, 29.65),
            (93.67, 39.67, 52.98),
            (84, 29, 31.69),
            (93.67, 39.67, 52.93),
            (85.67, 29.33, 32.11),
            (93.67, 39.67, 53.03),
            (83.33, 28.67, 31.38),
            (93.33, 39.33, 52.59),
            (84, 30.67, 32.74),
            (93.33, 40.67, 53.69),
            (83.33, 30.33, 32.40),
            (93.33, 41.33, 54.35),
        ],
        "Table 6A",
    )
    return {"table6A": table6}


def reader_contrasts():
    source = json.loads((ROOT / "data" / "statistics_inputs.json").read_text(encoding="utf-8"))
    indexed = {(r["dataset"], r["contrast"], r["K"]): r for r in source["reader_EM"]}
    contrast_names = [
        "second_title",
        "score_vs_order",
        "external_vs_no_cue",
        "morphology_vs_exact",
        "synonyms_vs_morphology",
        "family_vs_score",
    ]
    paper_values = {
        "2wiki": [
            (2.67, 1.0, 1.33, 4.33),
            (0.33, 2.33, 1.67, 2.0),
            (0.0, 1.0, 1.33, 0.33),
            (0.0, 0.33, 0.33, -0.33),
            (0.0, 0.0, 0.0, 0.0),
            (1.0, 0.67, 0.33, 0.33),
        ],
        "hotpotqa": [
            (-0.33, 1.0, 2.33, 1.0),
            (0.0, 0.67, 0.33, 0.0),
            (-0.67, 0.33, 0.0, 0.0),
            (-0.67, 0.0, 0.0, -0.33),
            (0.0, 0.0, 0.0, 0.0),
            (0.67, 0.0, 0.0, 0.0),
        ],
    }
    table6b = []
    for dataset in ["2wiki", "hotpotqa"]:
        for contrast, expected in zip(contrast_names, paper_values[dataset]):
            derived = []
            for k in [10, 20, 30, 50]:
                row = indexed[dataset, contrast, k]
                require(
                    row["n"] == row["wins"] + row["losses"] + row["ties"] == 300,
                    "Reader paired contingency mismatch",
                )
                delta = rounded(100 * (row["wins"] - row["losses"]) / row["n"])
                table6b.append(
                    {
                        "dataset": dataset,
                        "contrast": contrast,
                        "K": k,
                        "N": row["n"],
                        "wins": row["wins"],
                        "losses": row["losses"],
                        "EM_delta_pp": delta,
                    }
                )
                derived.append(delta)
            require(tuple(derived) == expected, "Table 6B contrast mismatch")
    return {"table6B": table6b}


def family_and_dedup():
    groups = defaultdict(list)
    for r in read_csv("family_pairs_k50.csv"):
        groups[r["dataset"]].append(r)
    table7a = []
    for dataset in ["2wiki", "hotpotqa"]:
        records = groups[dataset]
        require(len(records) == len({r["id"] for r in records}) == 300, "Family paired-ID mismatch")
        require(
            all(
                r["first_title_changed"] == r["selected_title_count_changed"] == "False"
                for r in records
            ),
            "Family title-control mismatch",
        )
        require(
            all(
                r["logical_calls_score"] == r["logical_calls_family"]
                and r["returned_records_score"] == r["returned_records_family"]
                for r in records
            ),
            "Family work-control mismatch",
        )
        output = {
            "dataset": dataset,
            "N": 300,
            "K": 50,
            "changed_queries": sum(r["query_changed"] == "True" for r in records),
        }
        for name, left, right in [
            ("pool", "score_pool_FT", "family_pool_FT"),
            ("title", "score_FT", "family_FT"),
            ("EM", "score_EM", "family_EM"),
        ]:
            before = [float(r[left]) for r in records]
            after = [float(r[right]) for r in records]
            output[name + "_before"] = int(sum(before))
            output[name + "_after"] = int(sum(after))
            output[name + "_wins"] = sum(b > a for a, b in zip(before, after))
            output[name + "_losses"] = sum(b < a for a, b in zip(before, after))
        table7a.append(output)
    compare(
        table7a,
        [
            "changed_queries",
            "pool_before",
            "pool_after",
            "pool_wins",
            "pool_losses",
            "title_before",
            "title_after",
            "title_wins",
            "title_losses",
            "EM_wins",
            "EM_losses",
        ],
        [(20, 265, 271, 7, 1, 252, 257, 5, 0, 3, 2), (8, 294, 294, 0, 0, 281, 281, 0, 0, 1, 1)],
        "Table 7A",
    )
    table7b = []
    for r in read_csv("dedup_counts_k50.csv"):
        output = {key: (value if key == "dataset" else int(value)) for key, value in r.items()}
        output["original_Score2_minus_Score1_pp"] = rounded(
            100 * (output["score2_original"] - output["score1_original"]) / output["N"]
        )
        output["single_Score2_minus_Score1_pp"] = rounded(
            100 * (output["score2_single"] - output["score1_single"]) / output["N"]
        )
        table7b.append(output)
    compare(
        table7b,
        [
            "versions_original",
            "versions_single",
            "unreachable_original",
            "unreachable_single",
            "score1_original",
            "score1_single",
            "score2_original",
            "score2_single",
            "original_Score2_minus_Score1_pp",
            "single_Score2_minus_Score1_pp",
        ],
        [
            (56687, 54957, 0, 25, 221, 204, 265, 244, 14.67, 13.33),
            (66635, 66581, 0, 0, 278, 278, 279, 280, 0.33, 0.67),
        ],
        "Table 7B",
    )
    return {"table7A": table7a, "table7B": table7b}


def reversed_reader():
    groups = defaultdict(list)
    for row in read_csv("reverse_reader_pairs.csv"):
        groups[row["dataset"], row["cue"], count(row, "K")].append(row)
    table8 = []
    for dataset, cue in [
        ("2wiki", "fewrel_exact"),
        ("2wiki", "fewrel_wordnet"),
        ("hotpotqa", "fewrel_exact"),
        ("hotpotqa", "fewrel_wordnet"),
    ]:
        for k in [10, 20, 30, 50]:
            records = groups[dataset, cue, k]
            require(
                len(records) == len({r["id"] for r in records}) == 300,
                "Reversal paired-ID mismatch",
            )
            output = {"dataset": dataset, "cue": cue, "K": k, "N": 300}
            for prefix in ["reference", "variant"]:
                for metric in ["EM", "F1"]:
                    values = [float(r[prefix + "_" + metric]) for r in records]
                    require(
                        all(0 <= v <= 1 and math.isfinite(v) for v in values),
                        "Invalid reader score",
                    )
                    output[prefix + "_" + metric] = rounded(100 * sum(values) / len(values))
            output["EM_wins"] = sum(
                float(r["variant_EM"]) > float(r["reference_EM"]) for r in records
            )
            output["EM_losses"] = sum(
                float(r["variant_EM"]) < float(r["reference_EM"]) for r in records
            )
            table8.append(output)
    compare(
        table8,
        ["reference_EM", "reference_F1", "variant_EM", "variant_F1"],
        [
            (27.67, 29.21, 27.67, 30),
            (29, 31.38, 30, 32.59),
            (27.67, 29.67, 30, 32.09),
            (29, 31.69, 30.67, 32.74),
            (27.67, 29.21, 27.67, 30),
            (29.33, 31.64, 29.67, 31.99),
            (28, 30.01, 29, 31.09),
            (28.67, 31.38, 30.33, 32.40),
            (33.33, 45.79, 31.67, 44.68),
            (36.67, 49.57, 37.67, 50.33),
            (40, 52.33, 39.33, 52.05),
            (39.67, 52.93, 40.67, 53.69),
            (32.67, 45.42, 31.33, 44.64),
            (36.67, 49.57, 38.33, 51),
            (40, 52.06, 39.67, 52.65),
            (39.33, 52.59, 41.33, 54.35),
        ],
        "Table 8",
    )
    compare(
        [r for r in table8 if r["K"] == 50],
        ["EM_wins", "EM_losses"],
        [(9, 4), (9, 4), (8, 5), (10, 4)],
        "Table 8 K50 paired EM",
    )
    return {"table8": table8}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, help="Directory for derived CSV tables and verification.json"
    )
    args = parser.parse_args()
    verify_hashes()
    tables = {}
    for build in [
        query_and_feedback,
        question_types,
        development,
        confirmation,
        reader_scores,
        reader_contrasts,
        family_and_dedup,
        reversed_reader,
    ]:
        tables.update(build())
    report = {
        "status": "PASS",
        "checks": CHECKS,
        "tables": {name: len(rows) for name, rows in tables.items()},
        "scope": "Saved numeric records and saved aggregates checked against paper table values.",
        "bootstrap_intervals_recomputed": False,
        "original_labels_reconstructed": False,
        "fresh_retrieval_or_reader_run": False,
        "root_verifier_required_for": [
            "Table 2 IDF contrasts",
            "Table 6 retained paired significance tests",
            "Table 9 nine-schedule study",
        ],
    }
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
        for name, rows in tables.items():
            with (args.output / (name + ".csv")).open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        (args.output / "verification.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        raise SystemExit("FAIL " + str(error))
