"""Descriptive checks on the two retained plans and the original-design rating pairs.

Run beside the VGA graph exports and Anonymous participant ratings.csv.
Uses only the Python standard library.
"""
import csv
from itertools import groupby
from pathlib import Path
from statistics import correlation, mean

ROOT = Path(__file__).resolve().parent

def read_rows(name):
    with (ROOT / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

def write_rows(name, rows):
    with (ROOT / name).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def average_ranks(values):
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    for _, tied in groupby(enumerate(order, 1), key=lambda entry: values[entry[1]]):
        entries = list(tied)
        rank = (entries[0][0] + entries[-1][0]) / 2
        for _, index in entries:
            ranks[index] = rank
    return ranks

def within_plan():
    results = []
    for plan, file in [("Original", "VGA Map 3.csv"), ("Adjusted", "VGA Map 1.csv")]:
        pairs = []
        for row in read_rows(file):
            length = float(row["Isovist Max Radial"]) / 1000
            clustering = float(row["Visual Clustering Coefficient"])
            if length >= 0 and 0 <= clustering <= 1:
                pairs.append((length, clustering))
        lengths, coefficients = zip(*pairs)
        results.append(dict(plan=plan, locations=len(pairs), mean_longest_sightline_m=mean(lengths),
                            mean_visual_clustering=mean(coefficients),
                            spearman_rho=correlation(average_ranks(lengths), average_ranks(coefficients))))
    write_rows("Within-plan visibility association.csv", results)

def permissible_scores(row):
    if row["score"]:
        return [int(row["score"])]
    low = int(row["lower"] or 1)
    high = int(row["upper"] or 5)
    if not 1 <= low <= high <= 5:
        raise ValueError("Rating outside the questionnaire scale")
    return range(low, high + 1)

def paired_bounds():
    rows = read_rows("Anonymous participant ratings.csv")
    by_person = {}
    for row in rows:
        by_person.setdefault((row["group"], row["participant"]), {})[row["variable"]] = row
    results = []
    for item in ["Scale", "Struct", "Presence"]:
        for group in ["Students", "Experts", "Combined"]:
            directions = []
            for (label, _), answers in by_person.items():
                if group != "Combined" and label != group:
                    continue
                video = permissible_scores(answers["Video_" + item])
                drawings = permissible_scores(answers["Drawings_" + item])
                directions.append({(v > d) - (v < d) for v in video for d in drawings})
            result = dict(item=item, group=group, n=len(directions))
            for value, label in [(-1, "drawings_higher"), (0, "tied"), (1, "video_clips_higher")]:
                result[label + "_min"] = sum(options == {value} for options in directions)
                result[label + "_max"] = sum(value in options for options in directions)
            result["video_minus_drawings_count_min"] = sum(min(opts) for opts in directions)
            result["video_minus_drawings_count_max"] = sum(max(opts) for opts in directions)
            results.append(result)
    write_rows("Paired rating direction bounds.csv", results)

if __name__ == "__main__":
    within_plan()
    paired_bounds()

