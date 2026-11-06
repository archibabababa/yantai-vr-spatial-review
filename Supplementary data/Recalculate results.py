"""Recalculate manuscript summaries from supplied, de-identified CSV records.
Standard library only. Never alters a source CSV or resolves ambiguous marks.
"""
from pathlib import Path
import csv,statistics as st,math,json,hashlib
B=Path(__file__).resolve().parent;O=B/'Recalculated';O.mkdir(exist_ok=True)
def read(name):
 with (B/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def number(x):
 try:return float(x)
 except (ValueError,TypeError):return None
def valid(x):return x is not None and 1<=x<=5
def mean(xs):return st.mean(xs) if xs else None
def quantile(xs,p):
 xs=sorted(xs);i=(len(xs)-1)*p;k=int(i);return xs[k]+(xs[min(k+1,len(xs)-1)]-xs[k])*(i-k)
ledger=read('Questionnaire rating provenance.csv')
assert len(ledger)==690
results=[]
for var in dict.fromkeys(r['variable'] for r in ledger):
 records=[r for r in ledger if r['variable']==var];ss=[r for r in records if r['group']=='学生'];ee=[r for r in records if r['group']!='学生']
 exact=[number(r['exact_value']) for r in ss];exact=[x for x in exact if valid(x)]
 bounds=[]
 for key in ['lower','upper']:
  vals=[]
  for r in ss:
   x=number(r['exact_value']);x=x if valid(x) else number(r[key])
   if valid(x):vals.append(x)
  bounds.append(mean(vals))
 a=[number(r['archive_A']) for r in ee];b=[number(r['archive_B']) for r in ee]
 results.append(dict(variable=var,student_n=len(exact),student_mean=mean(exact),student_sd=st.stdev(exact),student_median=st.median(exact),student_q1=quantile(exact,.25),student_q3=quantile(exact,.75),**{f'n{i}':exact.count(i) for i in range(1,6)},student_top2=sum(x>=4 for x in exact),lower_mean=bounds[0],upper_mean=bounds[1],archive_A_mean=mean([x for x in a if valid(x)]),archive_B_mean=mean([x for x in b if valid(x)]),archive_conflicts=sum(x!=y for x,y in zip(a,b))))
def write(name,rows):
 with (O/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
write('Questionnaire descriptive results.csv',results)

graphs={x:read(x+'.csv') for x in ['VGA Map 1','VGA Map 3','zx1','zx2']}
spec=[('Visual integration HH','Visual Integration [HH]','VGA Map 3','VGA Map 1'),('Visual mean depth','Visual Mean Depth','VGA Map 3','VGA Map 1'),('Visual connectivity','Connectivity','VGA Map 3','VGA Map 1'),('Visual clustering','Visual Clustering Coefficient','VGA Map 3','VGA Map 1'),('Axial integration HH','Integration [HH]','zx2','zx1'),('Axial integration HH R3','Integration [HH] R3','zx2','zx1'),('Axial mean depth','Mean Depth','zx2','zx1'),('Axial connectivity','Connectivity','zx2','zx1'),('Axial choice','Choice','zx2','zx1')]
sp=[]
for label,col,original,adjusted in spec:
 a=[float(r[col]) for r in graphs[original] if float(r[col])>=0];b=[float(r[col]) for r in graphs[adjusted] if float(r[col])>=0]
 sp.append(dict(metric=label,column=col,original_n=len(a),adjusted_n=len(b),original=st.mean(a),adjusted=st.mean(b),change=(st.mean(b)/st.mean(a)-1)*100))
write('Spatial metric results.csv',sp)
cor=[]
for name in ['zx2','zx1']:
 for label,col in [('Intelligibility','Connectivity'),('Synergy','Integration [HH] R3')]:
  xy=[(float(r[col]),float(r['Integration [HH]'])) for r in graphs[name] if float(r[col])>=0 and float(r['Integration [HH]'])>=0]
  x,y=zip(*xy);mx,my=st.mean(x),st.mean(y);xx=sum((v-mx)**2 for v in x);yy=sum((v-my)**2 for v in y);xyv=sum((a-mx)*(b-my) for a,b in zip(x,y));r=xyv/math.sqrt(xx*yy);slope=xyv/xx
  cor.append(dict(map=name,label=label,x=col,y='Integration [HH]',n=len(xy),r=r,r2=r*r,slope=slope,intercept=my-slope*mx))
write('Axial correlations.csv',cor)
checks=[]
for filename,calculated in [('Questionnaire descriptive results.csv',results),('Spatial metric results.csv',sp),('Axial correlations.csv',cor)]:
 supplied=read(filename);assert len(supplied)==len(calculated)
 for i,(a,b) in enumerate(zip(supplied,calculated)):
  for key,expected in a.items():
   actual=b[key];v=number(expected)
   if v is not None:
    assert actual is not None and math.isclose(v,float(actual),rel_tol=1e-10,abs_tol=1e-10),(filename,i,key,expected,actual)
   else:assert (expected==str(actual)) or (expected=='' and actual is None),(filename,i,key,expected,actual)
 checks.append({'file':filename,'rows':len(calculated),'matches_supplied':True})
inputs=[p for p in B.glob('*.csv')]
report={'checks':checks,'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}}
(O/'Recalculation checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checks,indent=2))

# Additional arithmetic bounds: no missing response is inserted into the data.
full=[]
for var in dict.fromkeys(r['variable'] for r in ledger if r['group']=='学生'):
 rows=[r for r in ledger if r['variable']==var and r['group']=='学生']
 low=[];high=[];exact=[];interval=0;unresolved=0
 for r in rows:
  x=number(r['exact_value'])
  if valid(x):low.append(x);high.append(x);exact.append(x)
  elif valid(number(r['lower'])) and valid(number(r['upper'])):
   low.append(number(r['lower']));high.append(number(r['upper']));interval+=1
  else:low.append(1);high.append(5);unresolved+=1
 full.append(dict(variable=var,cohort_n=15,exact_n=len(exact),interval_n=interval,unresolved_n=unresolved,exact_mean=mean(exact),all15_lower_mean=mean(low),all15_upper_mean=mean(high),min_high_count=sum(x>=4 for x in low),max_high_count=sum(x>=4 for x in high)))
vga=[]
for scheme,name in [('Original','VGA Map 3'),('Adjusted','VGA Map 1')]:
 rows=graphs[name];n=len(rows);conn=[float(r['Connectivity']) for r in rows]
 vga.append(dict(scheme=scheme,locations=n,mean_connectivity=mean(conn),mean_visible_fraction=mean(conn)/(n-1)))
for name,rows in [('Full student cohort sensitivity bounds.csv',full),('VGA graph size sensitivity.csv',vga)]:
 supplied=read(name)
 assert len(supplied)==len(rows)
 for a,b in zip(supplied,rows):
  for key,value in a.items():
   n=number(value)
   if n is not None:assert math.isclose(n,float(b[key]),rel_tol=1e-10,abs_tol=1e-10),(name,key,value,b[key])
   else:assert value==str(b[key])
 write(name,rows)
 checks.append({'file':name,'rows':len(rows),'matches_supplied':True})
report['checks']=checks
(O/'Recalculation checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checks[-2:],indent=2))
