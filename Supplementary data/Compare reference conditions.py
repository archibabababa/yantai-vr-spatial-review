"""Within-person ratings of the original design, keeping reference conditions separate.

Run with Python 3.10+ beside Anonymous participant ratings.csv. Each comparison
uses the same person and question. Bounds reflect response coding only.
"""
import csv
from itertools import product
from pathlib import Path


def read(path):
    with path.open(encoding="utf-8-sig",newline="") as src:
        return list(csv.DictReader(src))


def save(path,rows):
    with path.open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)


def values(row):
    if row["status"]=="point":return (int(row["score"]),)
    if row["status"]=="interval":return range(int(row["lower"]),int(row["upper"])+1)
    assert row["status"]=="unresolved"
    return range(1,6)


def calculate(src,out):
    records=read(src/"Anonymous participant ratings.csv")
    cells={(r['participant'],r['variable']):r for r in records}
    assert len(records)==len(cells)==690
    paired=[]; frequency=[]
    for cohort,reference in [('Experts','Prior site experience'),('Students','Photographs and renderings')]:
        people=sorted({r['participant'] for r in records if r['group']==cohort})
        assert len(people)==15
        for suffix in ('Scale','Struct','Presence'):
            for medium in ('Drawings','Video'):
                dirs=[]
                for p in people:
                    a,b=(values(cells[p,key+'_'+suffix]) for key in ('Reference',medium))
                    dirs.append({(x>y)-(x<y) for x,y in product(a,b)})
                row=dict(group=cohort,reference=reference,construct=suffix,comparator=medium,n=len(people))
                for label,v in [('reference_higher',1),('tie',0),('comparator_higher',-1)]:
                    row[label+'_min']=sum(d=={v} for d in dirs)
                    row[label+'_max']=sum(v in d for d in dirs)
                paired.append(row)
        for domain,ids in [('Reference items',{7,8,9}),('Other media items',{7,8,9}),
                           ('Revised scheme',set(range(10,16))),('VR tool',set(range(16,21)))]:
            rr=[r for r in records if r['group']==cohort and int(r['item'].split()[0][1:]) in ids]
            if domain in ('Reference items','Other media items'):
                rr=[r for r in rr if r['variable'].startswith('Reference_')==(domain=='Reference items')]
            row=dict(group=cohort,domain=domain,rating_slots=len(rr))
            for n in range(1,6):
                row['score_'+str(n)]=sum(r['status']=='point' and int(r['score'])==n for r in rr)
            row['interval_slots']=sum(r['status']=='interval' for r in rr)
            row['unresolved_slots']=sum(r['status']=='unresolved' for r in rr)
            assert sum(list(row.values())[3:])==len(rr)
            frequency.append(row)
    save(out/'Reference ratings against common media.csv',paired)
    save(out/'Rating frequencies by task.csv',frequency)


if __name__=='__main__':
    folder=Path(__file__).resolve().parent
    calculate(folder,folder)
