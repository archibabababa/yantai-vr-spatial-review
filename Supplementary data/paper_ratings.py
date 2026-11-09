from pathlib import Path
from collections import Counter
import csv
from statistics import mean

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def save(path,rows):
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def primary(root):
    rec=read(root/"Anonymous participant ratings.csv")
    for row in rec:
        if row["score"]!="":
            row["score"]=int(row["score"])
            assert 1<=row["score"]<=5
    return rec

def summary(record):
    result=[]
    for i in range(10,21):
        items=[r for r in record if r['item']==f'Q{i}']
        out=dict(item=i,variable=items[0]['variable'])
        for group in ('Students','Experts','Combined'):
            counts=Counter(r['score'] for r in items if (group=='Combined' or r['group']==group) and r['score']!='')
            for score in range(1,6):out[f'{group}_score{score}']=counts[score]
            out[f'{group}_high']=counts[4]+counts[5]
            out[f'{group}_n']=sum(counts.values())
        result.append(out)
    return result



def calculate(root):
    rec=primary(root)
    assert len(rec)==690 and sum(x['score']!='' for x in rec)==655
    cells={(r['participant'],r['variable']):r for r in rec}
    groups={g:sorted({r['participant'] for r in rec if r['group']==g}) for g in ('Students','Experts')}
    assert all(len(v)==15 for v in groups.values())
    scheme=summary(rec)
    for a in scheme:
        for group,ids in groups.items():
            z=[cells[i,a['variable']] for i in ids]
            partial=[r for r in z if r['score']=='']
            lo=sum(r['lower']!='' and int(float(r['lower']))>=4 for r in partial)
            hi=sum(r['upper']!='' and int(float(r['upper']))<=2 for r in partial)
            unknown=len(partial)-lo-hi
            a[group+'_interval45']=lo
            a[group+'_interval12']=hi
            a[group+'_unknown']=unknown
            a[group+'_yes_min']=a[group+'_high']+lo
            a[group+'_yes_max']=a[group+'_yes_min']+unknown
            assert sum(a[f'{group}_score{k}'] for k in range(1,6))+lo+hi+unknown==15
        for key in ('yes_min','yes_max'):a['Combined_'+key]=a['Students_'+key]+a['Experts_'+key]
    save(root/'Scheme and tool ratings by group.csv',scheme)
    comp=[('Drawings_Struct','Video_Struct'),('Video_Presence','Drawings_Presence'),
          ('VRSpace_Presence','Drawings_Presence'),('VRSpace_Struct','Drawings_Struct'),
          ('VRSpace_Scale','Drawings_Scale'),('Display','Comfort'),('Satisfaction','Function')]
    pairs=[]
    for a,b in comp:
        for g,ids in [*groups.items(),('Combined',groups['Students']+groups['Experts'])]:
            vals=[(cells[i,a]['score'],cells[i,b]['score']) for i in ids]
            dif=[x-y for x,y in vals if x!='' and y!='']
            pairs.append(dict(first_item=a,second_item=b,group=g,cohort=len(ids),complete_pairs=len(dif),
                              first_higher=sum(n>0 for n in dif),equal=dif.count(0),second_higher=sum(n<0 for n in dif),
                              without_two_point_scores=len(ids)-len(dif)))
    save(root/'Paired review comparisons.csv',pairs)
    matrix={}
    for r in rec:
        group='Architecture students' if r['group']=='Students' else 'Architectural experts'
        person=matrix.setdefault(r['participant'],{'Participant_ID':r['participant'],'Group':group})
        person[r['variable']]=r['score']
    save(root/'Expert and student rating matrix.csv',[matrix[k] for k in sorted(matrix)])
    means=[];bounds=[]
    for group,ids in groups.items():
        for name,suffix in [('Spatial scale','Scale'),('Spatial structure','Struct'),('Presence','Presence')]:
            row={'group':'Architectural experts' if group=='Experts' else 'Students','rating':name}
            for col,prefix in [('reference','Reference'),('drawings_original','Drawings'),('video_original','Video'),('vr_adjusted','VRSpace')]:
                vals=[cells[i,prefix+'_'+suffix]['score'] for i in ids if cells[i,prefix+'_'+suffix]['score']!='']
                row[col+'_mean']=format(mean(vals),'.2f');row[col+'_n']=len(vals)
            means.append(row)
    save(root/'Representation ratings by group.csv',means)
    for k in dict.fromkeys(r['variable'] for r in rec):
        z=[cells[i,k] for i in groups['Students']]
        val=[r['score'] for r in z if r['score']!='']
        partial=[r for r in z if r['score']=='']
        left=val+[int(float(r['lower'])) if r['lower'] else 1 for r in partial]
        right=val+[int(float(r['upper'])) if r['upper'] else 5 for r in partial]
        constrained=sum(bool(r['lower']) for r in partial)
        bounds.append(dict(variable=k,cohort_n=15,exact_n=len(val),interval_n=constrained,unresolved_n=len(partial)-constrained,exact_mean=mean(val),all15_lower_mean=mean(left),all15_upper_mean=mean(right),min_high_count=sum(x>=4 for x in left),max_high_count=sum(x>=4 for x in right)))
    save(root/'Full student cohort sensitivity bounds.csv',bounds)
    return rec,scheme,pairs

if __name__=='__main__':calculate(Path(__file__).resolve().parent)
