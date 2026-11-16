#!/usr/bin/env python3
"""Render the three paper figures from frozen, public aggregate inputs."""

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import re

import pypdfium2 as pdfium
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / "inputs"
FONT = "Times-Roman"
DATASETS = (("2wiki", "2Wiki"), ("hotpotqa", "HotpotQA"), ("musique", "MuSiQue"))
DENOMINATORS = {"2wiki": 12376, "hotpotqa": 7204, "musique": 2311}
BLUE = "#0072b2"
ORANGE = "#d55e00"
GREEN = "#009e73"
INK = "#18242f"
AXIS = "#64727d"
GRID = "#dce3e9"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(name):
    with (INPUTS / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def verify_input_hashes():
    sources = json.loads((ROOT / "SOURCES.json").read_text(encoding="utf-8"))
    hashes = {}
    for record in sources["distributed_inputs"]:
        path = ROOT / record["path"]
        actual = sha256(path)
        require(actual == record["sha256"], f"Input hash mismatch for {record['path']}")
        hashes[record["path"]] = actual
    return hashes


def matched_query_rows():
    rows = read_csv("matched_query_contrasts.csv")
    contrasts = {("no_second_branch", "repeat_q0_s2mask"), ("repeat_q0_s2mask", "hybrid_rrf")}
    expected = {(dataset, method, baseline, k) for dataset, _ in DATASETS
                for method, baseline in contrasts for k in range(1, 401)}
    indexed = {}
    for row in rows:
        key = (row["dataset"], row["method"], row["baseline"], int(row["K"]))
        require(key not in indexed, f"Duplicate Figure 1 row {key}")
        denominator = int(row["strict_valid_n"])
        wins, losses, ties = (int(row[name]) for name in ("wins", "losses", "ties"))
        require(min(wins, losses, ties) >= 0 and wins + losses + ties == denominator,
                f"Invalid paired counts for {key}")
        require(denominator == DENOMINATORS[row["dataset"]], f"Unexpected denominator for {key}")
        require(wins - losses == int(row["net_complete_n"]), f"Invalid paired net count for {key}")
        value = float(row["delta_pp"])
        require(math.isclose(value, 100 * (wins - losses) / denominator, abs_tol=1e-12),
                f"Invalid percentage-point difference for {key}")
        indexed[key] = value
    require(set(indexed) == expected and len(rows) == len(expected), "Figure 1 K grid differs")
    return indexed


def confirmation_rows():
    rows = read_csv("confirmation_curves.csv")
    expected = {(dataset, pool, k) for dataset, _ in DATASETS for pool in ("S2", "A")
                for k in range(1, 51)}
    indexed = {}
    for row in rows:
        key = (row["dataset"], row["pool"], int(row["K"]))
        require(key not in indexed, f"Duplicate Figure 2 row {key}")
        n, pool, before, after, wins, losses = (
            int(row[name]) for name in ("n", "pool_complete", "before", "after", "wins", "losses"))
        require(n == 1000 and 0 <= before <= pool <= n and 0 <= after <= pool,
                f"Invalid Figure 2 coverage counts for {key}")
        require(0 <= wins <= n - before and 0 <= losses <= before and after - before == wins - losses,
                f"Invalid Figure 2 paired counts for {key}")
        for field, count in (("pool_rate", pool), ("before_rate", before),
                             ("after_rate", after), ("delta_rate", wins - losses)):
            require(math.isclose(float(row[field]), count / n, abs_tol=1e-12),
                    f"Invalid Figure 2 rate {field} for {key}")
        indexed[key] = row
    require(set(indexed) == expected and len(rows) == len(expected), "Figure 2 K grid differs")
    for dataset, _ in DATASETS:
        for pool in ("S2", "A"):
            group = [indexed[dataset, pool, k] for k in range(1, 51)]
            require(len({row["pool_complete"] for row in group}) == 1, "Figure 2 pool ceiling changed")
            for field in ("before", "after"):
                counts = [int(row[field]) for row in group]
                require(counts == sorted(counts), f"Nonmonotone Figure 2 {field} coverage")
    return indexed


def reverse_curves():
    text = (INPUTS / "reverse_curves.tex").read_text(encoding="utf-8")
    blocks = re.split(r"\\nextgroupplot\[title=\{([^}]+)\}\]", text)
    require(len(blocks) == 5 and blocks[1::2] == ["2Wiki", "HotpotQA"], "Figure 3 panel titles differ")
    labels = ("Exact title", "Exact strict", "WordNet title", "WordNet strict")
    require(re.findall(r"\\addlegendentry\{([^}]+)\}", text) == list(labels),
            "Figure 3 legend order differs")
    indexed = {}
    plot_pattern = r"\\addplot\[([^]]+)\]\s+coordinates\s*\{([^}]+)\};"
    coordinate_pattern = r"\((\d+),(-?\d+(?:\.\d+)?)\)"
    for dataset, block_index in (("2wiki", 2), ("hotpotqa", 4)):
        plots = [(options, coordinates) for options, coordinates in re.findall(plot_pattern, blocks[block_index])
                 if "forget plot" not in options]
        require(len(plots) == 4, f"Figure 3 series count differs for {dataset}")
        for label, (options, coordinates) in zip(labels, plots):
            pairs = re.findall(coordinate_pattern, coordinates)
            remainder = re.sub(coordinate_pattern, "", coordinates).strip()
            require(not remainder and [int(k) for k, _ in pairs] == list(range(1, 51)),
                    f"Figure 3 coordinates differ for {dataset}/{label}")
            for k, value in pairs:
                numeric = float(value)
                require(math.isfinite(numeric) and -2 <= numeric <= 2, "Invalid Figure 3 coordinate")
                indexed[dataset, label, int(k)] = numeric
            require(("dashed" in options) == label.endswith("strict"), "Figure 3 line style differs")
    require(len(indexed) == 400, "Figure 3 requires 400 saved coordinates")
    return indexed


def label(pdf, x, y, text, size=9, align="left", color=INK):
    pdf.setFillColor(HexColor(color))
    pdf.setFont(FONT, size)
    methods = {"left": pdf.drawString, "center": pdf.drawCentredString, "right": pdf.drawRightString}
    methods[align](x, y, text)


def segment(pdf, x0, y0, x1, y1, color, width=0.5, dash=()):
    pdf.setStrokeColor(HexColor(color))
    pdf.setLineWidth(width)
    pdf.setDash(dash)
    pdf.line(x0, y0, x1, y1)
    pdf.setDash()


def y_label(pdf, x, y, text, size=8.5):
    pdf.saveState()
    pdf.translate(x, y)
    pdf.rotate(90)
    label(pdf, 0, 0, text, size, "center")
    pdf.restoreState()


def legend_entry(pdf, x, y, text, color, dash=(), size=9):
    segment(pdf, x, y, x + 20, y, color, 1.2, dash)
    label(pdf, x + 25, y - 2.8, text, size)


def curve(pdf, points, color, dash=(), width=1.2):
    require(len(points) >= 2 and all(math.isfinite(v) for point in points for v in point),
            "Invalid plotted coordinates")
    path = pdf.beginPath()
    path.moveTo(*points[0])
    for point in points[1:]:
        path.lineTo(*point)
    pdf.setStrokeColor(HexColor(color))
    pdf.setLineWidth(width)
    pdf.setDash(dash)
    pdf.drawPath(path, stroke=1, fill=0)
    pdf.setDash()


def record_series(records, figure, dataset, pool, series, ks, values):
    require(len(ks) == len(values), "Plotted K/value lengths differ")
    for k, value in zip(ks, values):
        require(math.isfinite(value), "Nonfinite plotted value")
        records.append({"figure": figure, "dataset": dataset, "pool": pool, "series": series,
                        "K": k, "value_pp_or_percent": value})


def new_pdf(output, name, height):
    pdf = canvas.Canvas(str(output / f"{name}.pdf"), pagesize=(510, height),
                        invariant=1, initialFontName=FONT)
    pdf.setTitle(name)
    pdf.setAuthor("")
    return pdf


def plot_matched_query(output, data, records):
    """Preserve the original single-row ReportLab layout and log K axis."""
    pdf = new_pdf(output, "matched_query_fullk", 228)
    specs = (("S2 - matched Repeat", "no_second_branch", "repeat_q0_s2mask", BLUE, ()),
             ("Matched Repeat - RRF", "repeat_q0_s2mask", "hybrid_rrf", ORANGE, (4, 2)))
    for x, spec in zip((56, 290), specs):
        legend_entry(pdf, x, 216, spec[0], spec[3], spec[4], 8.8)
    limits = ((-10, 45), (-15, 10), (-10, 15))
    ticks = ((-10, 0, 10, 20, 30, 40), (-15, -10, -5, 0, 5, 10), (-10, -5, 0, 5, 10, 15))
    ks = list(range(1, 401))
    for column, (dataset, title) in enumerate(DATASETS):
        left, bottom, top = 43 + 162 * column, 35, 178
        low, high = limits[column]
        def x_at(k):
            return left + math.log(k) / math.log(400) * 128
        def y_at(value):
            return bottom + (value - low) / (high - low) * (top - bottom)
        label(pdf, left + 64, 195, title, 9.5, "center")
        for value in ticks[column]:
            segment(pdf, left, y_at(value), left + 128, y_at(value), AXIS if value == 0 else GRID,
                    0.65 if value == 0 else 0.35)
            label(pdf, left - 4, y_at(value) - 2.7, str(value), 8.4, "right", AXIS)
        segment(pdf, left, bottom, left + 128, bottom, AXIS)
        for k in (1, 2, 5, 10, 50, 100, 400):
            segment(pdf, x_at(k), bottom, x_at(k), bottom - 3, AXIS)
            label(pdf, x_at(k), bottom - 13, str(k), 8.4, "center", AXIS)
        segment(pdf, x_at(50), bottom, x_at(50), top, "#a7afb6", dash=(2, 3))
        for title, method, baseline, color, dash in specs:
            values = [data[dataset, method, baseline, k] for k in ks]
            require(all(low <= value <= high for value in values), "Figure 1 value outside saved axis")
            curve(pdf, [(x_at(k), y_at(value)) for k, value in zip(ks, values)], color, dash)
            record_series(records, 1, dataset, "", title, ks, values)
        label(pdf, left + 64, bottom - 29, "K (log scale)", 8.6, "center")
    y_label(pdf, 10, 106.5, "Complete-coverage difference (pp)")
    pdf.save()


def plot_confirmation(output, data, records):
    """Preserve the original 2-by-3 layout, limits, colors and K=5 markers."""
    pdf = new_pdf(output, "confirmation_fixed_pool_K1_50", 340)
    styles = (("Before", BLUE, ()), ("Frozen reranking", ORANGE, (4, 2)),
              ("Shared pool ceiling", GREEN, (1.5, 2)))
    for x, (title, color, dash) in zip((58, 209, 371), styles):
        legend_entry(pdf, x, 326, title, color, dash)
    ks = list(range(1, 51))
    for row, pool in enumerate(("S2", "A")):
        bottom, top = ((198, 282), (42, 126))[row]
        heading = "(a) S2 candidate pool" if pool == "S2" else "(b) A candidate pool; reranked A is C"
        label(pdf, 44, top + 29, heading, 9.5)
        y_label(pdf, 11, (bottom + top) / 2, "Complete-support coverage (%)", 9)
        for column, (dataset, title) in enumerate(DATASETS):
            left = 44 + column * 163
            def x_at(k):
                return left + (k - 1) / 49 * 130
            def y_at(value):
                return bottom + value / 100 * (top - bottom)
            label(pdf, left + 65, top + 13, title, 9.5, "center")
            for value in range(0, 101, 20):
                segment(pdf, left, y_at(value), left + 130, y_at(value), GRID, 0.35)
                label(pdf, left - 5, y_at(value) - 2.8, str(value), 8.5, "right", AXIS)
            segment(pdf, left, bottom, left + 130, bottom, AXIS)
            for k in (1, 5, 10, 20, 30, 40, 50):
                segment(pdf, x_at(k), bottom, x_at(k), bottom - 2.5, AXIS)
                label(pdf, x_at(k), bottom - 13, str(k), 8.5, "center", AXIS)
            label(pdf, left + 65, bottom - 27, "Output capacity K", 9, "center")
            segment(pdf, x_at(5), bottom, x_at(5), top, "#9aa5ae", dash=(2, 3))
            for series, field, color, dash in (
                    ("Shared pool ceiling", "pool_rate", GREEN, (1.5, 2)),
                    ("Before", "before_rate", BLUE, ()),
                    ("Frozen reranking", "after_rate", ORANGE, (4, 2))):
                values = [100 * float(data[dataset, pool, k][field]) for k in ks]
                curve(pdf, [(x_at(k), y_at(value)) for k, value in zip(ks, values)], color, dash, 1.3)
                if field != "pool_rate":
                    pdf.setFillColor(HexColor(color))
                    pdf.circle(x_at(5), y_at(values[4]), 1.8, stroke=0, fill=1)
                record_series(records, 2, dataset, pool, series, ks, values)
    pdf.save()


def plot_reverse(output, data, records):
    """Replay all saved TeX coordinates with the original two-panel structure."""
    pdf = new_pdf(output, "reverse_curves", 212)
    specs = (("Exact title", "#0000bf", ()), ("Exact strict", "#0000bf", (4, 2)),
             ("WordNet title", "#d96c00", ()), ("WordNet strict", "#d96c00", (4, 2)))
    for x, (title, color, dash) in zip((42, 153, 266, 390), specs):
        legend_entry(pdf, x, 198, title, color, dash, 8.5)
    ks = list(range(1, 51))
    for column, (dataset, title) in enumerate(DATASETS[:2]):
        left, bottom, top, width = 47 + column * 248, 39, 162, 195
        def x_at(k):
            return left + (k - 1) / 49 * width
        def y_at(value):
            return bottom + (value + 2) / 4 * (top - bottom)
        label(pdf, left + width / 2, 177, title, 10, "center")
        for value in (-2, -1, 0, 1, 2):
            segment(pdf, left, y_at(value), left + width, y_at(value), GRID, 0.35)
            label(pdf, left - 6, y_at(value) - 3, str(value), 9, "right", AXIS)
        for k in (1, 10, 20, 30, 40, 50):
            segment(pdf, x_at(k), bottom, x_at(k), top, GRID, 0.35)
            label(pdf, x_at(k), bottom - 14, str(k), 9, "center", AXIS)
        segment(pdf, left, bottom, left, top, AXIS)
        segment(pdf, left, bottom, left + width, bottom, AXIS)
        segment(pdf, left, y_at(0), left + width, y_at(0), "#808080", 0.6, (1, 2))
        for series, color, dash in specs:
            values = [data[dataset, series, k] for k in ks]
            curve(pdf, [(x_at(k), y_at(value)) for k, value in zip(ks, values)], color, dash)
            record_series(records, 3, dataset, "", series, ks, values)
        label(pdf, left + width / 2, bottom - 30, "Retained documents K", 9, "center")
        y_label(pdf, left - 29, (bottom + top) / 2, "Reverse minus original (pp)", 9)
    pdf.save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Directory for generated PDFs, PNGs and reports")
    parser.add_argument("--scale", type=float, default=2.5, help="PNG pixels per PDF point, default 2.5")
    args = parser.parse_args()
    require(math.isfinite(args.scale) and args.scale > 0, "PNG scale must be finite and positive")
    hashes = verify_input_hashes()
    matched = matched_query_rows()
    confirmation = confirmation_rows()
    reverse = reverse_curves()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    records = []
    plot_matched_query(output, matched, records)
    plot_confirmation(output, confirmation, records)
    plot_reverse(output, reverse, records)
    counts = Counter(row["figure"] for row in records)
    require(counts == {1: 2400, 2: 900, 3: 400}, "Plotted point counts differ")
    with (output / "plotted_data.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    outputs = []
    names = ("matched_query_fullk", "confirmation_fixed_pool_K1_50", "reverse_curves")
    for number, name in enumerate(names, 1):
        path = output / f"{name}.pdf"
        document = pdfium.PdfDocument(str(path))
        require(len(document) == 1, f"Unexpected PDF page count for {name}")
        page = document[0]
        bitmap = page.render(scale=args.scale)
        bitmap.to_pil().save(output / f"{name}.png")
        outputs.append({"figure": number, "pdf": path.name, "pdf_sha256": sha256(path),
                        "png": f"{name}.png", "plotted_points": counts[number],
                        "width_pt": page.get_width(), "height_pt": page.get_height()})
        bitmap.close()
        page.close()
        document.close()
    report = {"status": "PASS", "scope": "Saved-aggregate figure rendering and saved TeX coordinate replay",
              "input_sha256": hashes, "script_sha256": sha256(Path(__file__)),
              "plotted_data_sha256": sha256(output / "plotted_data.csv"),
              "plotted_points": len(records), "font": FONT, "figures": outputs,
              "checks": ["Distributed input SHA-256", "Complete dataset/condition/K grids",
                         "Figure 1 paired counts and percentage-point differences",
                         "Figure 2 counts, rates, fixed ceilings and monotone coverage",
                         "Figure 3 exact saved TeX coordinate sequence and series styles",
                         "3700 plotted values and three one-page rendered PDFs"],
              "rendering_changes": "Portable Times-Roman font. Figure 3 uses ReportLab in place of PGFPlots."}
    (output / "plot_verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "plotted_points": len(records), "output": str(output)}))


if __name__ == "__main__":
    main()
