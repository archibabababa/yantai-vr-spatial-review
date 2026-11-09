"""Paired Q9 ratings and itemwise dispersion for the same two groups of fifteen.

Uses only Python's standard library. Counts are bounded over every integer
assignment allowed by the source entries; no values are filled in.
"""
import csv
from collections import Counter
from itertools import product
from pathlib import Path


def load(folder):
    with (folder/'Anonymous participant ratings.csv').open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def save(path, data):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer=csv.DictWriter(f,fieldnames=data[0])
        writer.writeheader()
        writer.writerows(data)


def possibilities(row):
    if row['status']=='point':
        return [int(row['score'])]
    if row['status']=='interval':
        return range(int(row['lower']),int(row['upper'])+1)
    assert row['status']=='unresolved'
    return range(1,6)


def calculate(folder):
    records=load(folder)
    cells={(r['participant'],r['variable']):r for r in records}
    ids={r['participant']:r['group'] for r in records}
    assert len(records)==len(cells)==690 and Counter(ids.values())=={'Students':15,'Experts':15}
    variables=list(dict.fromkeys(r['variable'] for r in records))
    spread=[];paired=[]
    for group in ['Students','Experts','All']:
        people=[p for p in sorted(ids) if group=='All' or ids[p]==group]
        for label in ['Drawings','Video clips','Higher of drawings and clips']:
            deltas=[]
            for p in people:
                vr,draw,clip=[possibilities(cells[p,k+'_Presence']) for k in ('VRSpace','Drawings','Video')]
                vals=set()
                for v,d,c in product(vr,draw,clip):
                    comp=d if label=='Drawings' else c if label=='Video clips' else max(d,c)
                    vals.add(v-comp)
                deltas.append(vals)
            directions=[{(v>0)-(v<0) for v in vals} for vals in deltas]
            result=dict(group=group,participants=len(people),comparator=label)
            for key,direction in [('VR_higher',1),('equal',0),('VR_lower',-1)]:
                result[key+'_min']=sum(v=={direction} for v in directions)
                result[key+'_max']=sum(direction in v for v in directions)
            result['mean_paired_difference_min']=sum(min(v) for v in deltas)/len(people)
            result['mean_paired_difference_max']=sum(max(v) for v in deltas)/len(people)
            paired.append(result)
        if group=='All':continue
        for var in variables:
            obs=[cells[p,var] for p in people]
            row=dict(group=group,item=obs[0]['item'],variable=var,n=15)
            for i in range(1,6):
                row['score_'+str(i)]=sum(r['status']=='point' and int(r['score'])==i for r in obs)
            row['interval_1_2']=sum(r['status']=='interval' and r['lower']=='1' for r in obs)
            row['interval_4_5']=sum(r['status']=='interval' and r['lower']=='4' for r in obs)
            row['unresolved']=sum(r['status']=='unresolved' for r in obs)
            assert sum(list(row.values())[4:])==15
            stats=[]
            for assignment in product(*(possibilities(r) for r in obs)):
                values=sorted(assignment);counts=Counter(values)
                unequal=105-sum(k*(k-1)//2 for k in counts.values())
                stats.append((values[3],values[7],values[11],unequal))
            for j,key in enumerate(['Q1','median','Q3','unequally_rated_pairs']):
                row[key+'_min']=min(s[j] for s in stats)
                row[key+'_max']=max(s[j] for s in stats)
            row['possible_pairs']=105
            spread.append(row)
    save(folder/'VR presence comparisons.csv',paired)
    save(folder/'Score frequencies and dispersion.csv',spread)
    return paired,spread


if __name__=='__main__':
    calculate(Path(__file__).resolve().parent)
