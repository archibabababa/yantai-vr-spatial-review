"""Describe horizontal visibility around the three landmarks in manuscript Figure 4.

Run with Python 3.10+ beside the two VGA exports and Technical sources/Drawing1.dxf.
Optional input and output directories make it possible to reproduce the analysis
without changing the source data. All geometry is in metres in the CAD frame.
"""
import argparse
import csv
import struct
from pathlib import Path
from statistics import median

MAPS = ("VGA Map 3.csv", "VGA Map 1.csv")
FLIGHTS = (("1AC3", "1AF9"), ("1491", "1B87"))
STEPS = (("18CE", "18D5"), ("1647", "164D"))
LABELS = ("Anteroom", "Approach stair", "Broad steps")
RADII = (0.6, 1.2, 2.4)


def read_lines(drawing):
    raw = drawing.read_text(encoding="utf-8", errors="replace").splitlines()
    pairs = [(int(k), v.strip()) for k, v in zip(raw[::2], raw[1::2])]
    assert pairs[pairs.index((9, "$INSUNITS")) + 1] == (70, "4")
    handles = {handle for pair in FLIGHTS + STEPS for handle in pair}
    lines = {}
    for i, (code, value) in enumerate(pairs):
        if code != 5 or value not in handles or pairs[i - 1] != (0, "LINE"):
            continue
        end = next(j for j in range(i + 1, len(pairs)) if pairs[j][0] == 0)
        entity = dict(pairs[i:end])
        lines[value] = tuple(complex(float(entity[x]), float(entity[y])) / 1000
                             for x, y in [(10, 20), (11, 21)])
    assert set(lines) == handles
    return lines


def grid(path, native):
    points = []
    title = path.stem.encode("ascii")
    assert native.count(title) == 1
    header = native.index(title) + len(title)
    pitch, ny, nx, count, west, south = struct.unpack_from("<diiidd", native, header)
    assert pitch == 600 and (west, south) == (-130800, -1200)
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            key = int(row["key"])
            ix, iy = key >> 16, key & 65535
            assert 0 <= ix < nx and 0 <= iy < ny
            pos = complex(ix * pitch + west, iy * pitch + south) / 1000
            length = float(row["Isovist Max Radial"]) / 1000
            cluster = float(row["Visual Clustering Coefficient"])
            assert length >= 0 and 0 <= cluster <= 1
            points.append((key, pos, length, cluster))
    assert len({p[0] for p in points}) == len(points) == count
    return points


def locations(lines, grids, tread_index=0):
    # Transfer the Figure 4 author-identified approximate area, using the
    # same homologous tread ends and the translation/rotation/scale of that tread.
    grid = grids[1]
    adjusted = complex(min(r[1].real for r in grid) + 28.4,
                       min(r[1].imag for r in grid) + 41.3)
    a, b = sorted(lines[STEPS[1][tread_index]], key=lambda p: p.real)
    c, d = sorted(lines[STEPS[0][tread_index]], key=lambda p: p.real)
    original = c + (adjusted - a) * (d - c) / (b - a)

    def centre(pair):
        return sum(p for handle in pair for p in lines[handle]) / 4

    return [(target, centre(flight), centre(steps))
            for target, flight, steps in zip((original, adjusted), FLIGHTS, STEPS)]


def save(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)


def analyse(src, out):
    native = (src / "Technical sources/sy.graph").read_bytes()
    graphs = [grid(src / f, native) for f in MAPS]
    assert [len(g) for g in graphs] == [5320, 6334]
    lines = read_lines(src / "Technical sources/Drawing1.dxf")
    centres = locations(lines, graphs)
    summary, membership = [], []
    for design, points, anchors in zip(("Original", "Adjusted"), graphs, centres):
        for marker, (label, centre) in enumerate(zip(LABELS, anchors), 1):
            distances = sorted((abs(p - centre), key, ray, cluster)
                               for key, p, ray, cluster in points)
            for dist, key, ray, cluster in distances:
                if dist > max(RADII) + 1e-9:
                    break
                membership.append(dict(design=design, marker=marker, key=key,
                                       distance_m=dist, longest_sightline_m=ray,
                                       visual_clustering=cluster))
            for radius in RADII:
                subset = [row for row in distances if row[0] <= radius + 1e-9]
                summary.append(dict(design=design, marker=marker, landmark=label,
                                    centre_cad_x_m=centre.real, centre_cad_y_m=centre.imag,
                                    radius_m=radius, sampled_positions=len(subset),
                                    nearest_grid_distance_m=distances[0][0],
                                    median_longest_sightline_m=median(r[2] for r in subset) if subset else "",
                                    median_visual_clustering=median(r[3] for r in subset) if subset else ""))
    out.mkdir(parents=True, exist_ok=True)
    save(out / "Landmark visibility.csv", summary)
    save(out / "Landmark grid membership.csv", membership)
    # Shift the original anteroom registration to a second saved stair tread.
    # The author-marked target in the adjusted plan is identical in both registrations.
    anchor = locations(lines, graphs, tread_index=1)[0][0]
    alternate = []
    for radius in RADII:
        rows = [p for p in graphs[0] if abs(p[1] - anchor) <= radius + 1e-9]
        alternate.append(dict(design="Original", marker=1, reference_original="18D5",
                              reference_adjusted="164D", centre_cad_x_m=anchor.real,
                              centre_cad_y_m=anchor.imag, centre_shift_m=abs(anchor-centres[0][0]),
                              radius_m=radius, sampled_positions=len(rows),
                              median_longest_sightline_m=median(p[2] for p in rows),
                              median_visual_clustering=median(p[3] for p in rows)))
    save(out / "Anteroom registration check.csv", alternate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    parser.add_argument("--input", type=Path, default=here)
    parser.add_argument("--output", type=Path, default=here)
    args = parser.parse_args()
    analyse(args.input, args.output)
