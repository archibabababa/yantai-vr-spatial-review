"""Reproduce landmark-to-landmark intervisibility and same-person task preferences.

Python 3.10+. Run beside the published graph exports and anonymous questionnaire.
The reader supports the archived version-440 point maps only. Its field order follows
the upstream mgraph440 format (SpaceGroupUCL/depthmapX: pointmap.cpp, point.cpp,
attributes.cpp, ngraph.cpp and pixelref.h). No line-of-sight paths are simulated.
"""
import argparse
import csv
import math
from itertools import combinations, product
from pathlib import Path
import struct


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def save(path, data):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=data[0])
        writer.writeheader()
        writer.writerows(data)


class Reader:
    def __init__(self, data, offset):
        self.data, self.offset = data, offset

    def take(self, fmt):
        spec = struct.Struct("<" + fmt)
        result = spec.unpack_from(self.data, self.offset)
        self.offset += spec.size
        return result[0] if len(result) == 1 else result

    def skip_string(self):
        size = self.take("I")
        assert size < 65536
        self.offset += size


def read_edges(data, title, target, degree):
    title_bytes = title.encode("ascii")
    assert data[:7] == b"grf" + struct.pack("<I", 440) and data.count(title_bytes) == 1
    reader = Reader(data, data.index(title_bytes) + len(title_bytes))
    pitch, ny, nx, count, west, south = reader.take("diiidd")
    assert count == len(degree) and pitch == 600
    reader.take("iqq")
    for _ in range(reader.take("i")):
        reader.take("q")
        reader.skip_string()
    nc = reader.take("i")
    for _ in range(nc):
        reader.skip_string()
        reader.take("ffdi??ffi")
        reader.skip_string()
    assert reader.take("i") == count
    for _ in range(count):
        key, _, n = reader.take("iqi")
        assert n == nc and key in degree
        reader.offset += n * 4
    reader.offset += 12  # Reference-column display settings.
    neighbours = {}
    seen = set()
    for ix in range(nx):
        for iy in range(ny):
            key = (ix << 16) | iy
            state, block, misc, adjacent, merge, has_node = reader.take("iiiBiB")
            assert has_node in (0, 1)
            if has_node:
                assert key in degree
                seen.add(key)
                encoded_degree = 0
                for _ in range(32):
                    direction, size, farthest, occlusion = reader.take("BHff")
                    encoded_degree += size
                    if not size:
                        continue
                    assert direction in (1,2,4,8)
                    runs = 1 if direction in (4,8) else reader.take("H")
                    assert runs >= 1
                    if key not in target:
                        reader.offset += 6 + 4 * (runs-1)
                        continue
                    edges = neighbours.setdefault(key,set())
                    startx, starty, span = reader.take("hhH")
                    segment_count = 0
                    for j in range(runs):
                        if j:
                            primary, packed = reader.take("hH")
                            shift, span = packed & 15, packed >> 4
                            if direction == 1:
                                startx, starty = primary, starty+shift
                            else:
                                startx, starty = startx+shift, primary
                        dx,dy={1:(1,0),2:(0,1),4:(1,1),8:(1,-1)}[direction]
                        edges.update(((startx+k*dx)<<16)|(starty+k*dy) for k in range(span+1))
                        segment_count += span+1
                    assert segment_count == size
                assert encoded_degree == degree[key], (title,key,encoded_degree,degree[key])
                for _ in range(32):
                    n = reader.take("I")
                    reader.offset += n*4
            loc_x,loc_y = reader.take("dd")
            if key in target:
                assert abs(loc_x-(west+pitch*ix)) < .01 and abs(loc_y-(south+pitch*iy)) < .01
    assert seen == set(degree) and set(neighbours) == target
    return neighbours


def spatial(src):
    native=(src/"Technical sources/sy.graph").read_bytes()
    member=rows(src/"Landmark grid membership.csv")
    sensitivity=rows(src/"Anteroom registration check.csv")
    output=[]
    diagnostics=[]
    for design, title in [("Original","VGA Map 3"),("Adjusted","VGA Map 1")]:
        attributes={int(r["key"]):r for r in rows(src/(title+".csv"))}
        degree={k:int(float(r["Connectivity"])) for k,r in attributes.items()}
        loc={(k):complex((k>>16)*.6-130.8,(k&65535)*.6-1.2) for k in degree}
        near={m:{int(r["key"]):float(r["distance_m"]) for r in member
                 if r["design"]==design and int(r["marker"])==m} for m in (1,2,3)}
        zone_options=[("Figure 4",near)]
        if design=="Original":
            p=sensitivity[0]
            anchor=complex(float(p["centre_cad_x_m"]),float(p["centre_cad_y_m"]))
            alt={k:abs(v-anchor) for k,v in loc.items() if abs(v-anchor)<=2.4+1e-9}
            zone_options.append(("Second tread",{**near,1:alt}))
        target=set().union(*(set(nodes) for _,zones in zone_options for nodes in zones.values()))
        graph=read_edges(native,title,target,degree)
        domain=set(attributes)
        errors={}
        structural={}
        for k,edges in graph.items():
            squared=[((j>>16)-(k>>16))**2+((j&65535)-(k&65535))**2 for j in edges]
            first=sum(math.sqrt(d)*600 for d in squared)
            second=sum(squared)*600**2
            raw=[float(attributes[k][n]) for n in ('Point First Moment','Point Second Moment')]
            errors[k]=max(abs(value/ref-1) for value,ref in zip((first,second),raw))
            structural[k]=len(edges)==degree[k] and k not in edges and edges<=domain
            diagnostics.append(dict(design=design,key=k,exported_degree=degree[k],decoded_unique=len(edges),
                     outside_domain=len(edges-domain),self_link=int(k in edges),
                     distance_sum_mm=first,archived_first_moment=raw[0],
                     squared_distance_sum_mm2=second,archived_second_moment=raw[1],max_relative_error=errors[k]))
        for registration,zones in zone_options:
            for radius in (.6,1.2,2.4):
                parts={m:{k for k,d in zones[m].items() if d <=radius+1e-9} for m in (1,2,3)}
                for a,b in combinations(parts,2):
                    if registration=="Second tread" and a!=1:continue
                    first,second=parts[a],parts[b]
                    assert first and second and first.isdisjoint(second)
                    n=len(first)*len(second)
                    for tol in (0.00001,0.00005):
                        found=unresolved=0
                        covered=set()
                        possibly_covered=set()
                        for i,j in product(first,second):
                            forward,reverse=j in graph[i],i in graph[j]
                            verified=any(structural[k] and errors[k]<=tol for k in (i,j))
                            if not verified or forward!=reverse:
                                unresolved+=1
                                possibly_covered.add(i)
                            elif forward:
                                found+=1
                                covered.add(i)
                        output.append(dict(design=design,registration=registration,radius_m=radius,
                                    moment_relative_tolerance=tol,landmark_a=a,landmark_b=b,
                                    n_a=len(first),n_b=len(second),possible_pairs=n,
                                    visible_min=found,visible_max=found+unresolved,unresolved=unresolved,
                                    fraction_min=found/n,fraction_max=(found+unresolved)/n,
                                    a_points_seeing_any_b_min=len(covered),
                                    a_points_seeing_any_b_max=len(covered|possibly_covered)))
    return output,diagnostics


def review_tasks(src):
    ratings=rows(src/"Anonymous participant ratings.csv")
    people={r["participant"]:r["group"] for r in ratings}
    assert set(people.values())=={"Students","Experts"} and sum(g=="Students" for g in people.values())==15 and len(people)==30
    cells={(r["participant"],r["variable"]):r for r in ratings}
    def options(row):
        if row["status"]=="point":return [int(row["score"])]
        if row["status"]=="interval":return range(int(row["lower"]),int(row["upper"])+1)
        assert row["status"]=="unresolved"
        return range(1,6)
    patterns={}
    for p in people:
        values=[]
        for construct in ("Struct","Presence"):
            drawing,clip=(options(cells[p,prefix+construct]) for prefix in ("Drawings_","Video_"))
            values.append({(a>b)-(a<b) for a,b in product(drawing,clip)})
        patterns[p]=set(product(*values))
    out=[]
    labels={1:"drawings higher",0:"tie",-1:"clips higher"}
    for group in ("Students","Experts","Combined"):
        sub=[v for p,v in patterns.items() if group=="Combined" or people[p]==group]
        for structure,presence in product((1,0,-1),repeat=2):
            pat=(structure,presence)
            out.append(dict(group=group,people=len(sub),structure=labels[structure],
                            presence=labels[presence],count_min=sum(v=={pat} for v in sub),
                            count_max=sum(pat in v for v in sub)))
    return out


def comfort_among_joint(src):
    data=rows(src/"Anonymous participant ratings.csv")
    by_person={}
    for row in data:
        if row["variable"] not in ("Circulation","Display","Comfort"):continue
        if row["status"]=="point":lo=hi=int(row["score"])
        elif row["status"]=="interval":lo,hi=int(row["lower"]),int(row["upper"])
        else:lo,hi=1,5
        assert lo>=4 or hi<4  # High versus non-high is known for these three items.
        by_person.setdefault((row["group"],row["participant"]),{})[row["variable"]]=lo>=4
    result=[]
    for group in ("Students","Experts"):
        group_rows=[p for (g,k),p in by_person.items() if g==group]
        assert len(group_rows)==15
        joint=[p for p in group_rows if p["Circulation"] and p["Display"]]
        comfortable=sum(p["Comfort"] for p in joint)
        result.append(dict(group=group,participants=len(group_rows),both_circulation_display_high=len(joint),
                           also_high_comfort=comfortable,comfort_below_four=len(joint)-comfortable))
    return result


def main(src,out):
    out.mkdir(exist_ok=True,parents=True)
    links,checks=spatial(src)
    save(out/"Direct visibility between landmarks.csv",links)
    save(out/"Landmark node checks.csv",checks)
    save(out/"Paired media tasks by reviewer.csv",review_tasks(src))
    save(out/"Comfort among joint endorsements.csv",comfort_among_joint(src))


if __name__=="__main__":
    here=Path(__file__).resolve().parent
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,default=here)
    parser.add_argument("--output",type=Path,default=here)
    args=parser.parse_args()
    main(args.input,args.output)
