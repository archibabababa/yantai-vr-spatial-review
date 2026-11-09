from pathlib import Path
import csv,statistics as st,math
from statistics import mean
B=Path(__file__).resolve().parent
def read(name):
    with (B/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows):
    with (B/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
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

def exterior(root):
    # West/east/south/north extremal vertices on the evaluated level in each saved plan.
    # LINE handle + 0 (start) or 1 (end). Coordinates converted from mm to m.
    limits={'Original': [('17D7',1),('17DC',1),('17F1',0),('17CB',1)],
            'Adjusted': [('15A0',0),('1541',1),('15BB',0),('14D9',1)]}
    raw=(root/'Technical sources/Drawing1.dxf').read_text(encoding='utf8',errors='replace').splitlines()
    pairs=[(int(k),v.strip()) for k,v in zip(raw[::2],raw[1::2])]
    assert pairs[pairs.index((9,'$INSUNITS'))+1]==(70,'4')
    result=[]
    for design,coords in limits.items():
        pts=[]
        for handle,endpt in coords:
            i=pairs.index((5,handle));j=next(k for k in range(i+1,len(pairs)) if pairs[k][0]==0)
            assert pairs[i-1]==(0,'LINE')
            d=dict(pairs[i:j])
            pts.append((float(d[10+endpt])/1000,float(d[20+endpt])/1000))
        result.append(dict(design=design,west=coords[0][0],east=coords[1][0],south=coords[2][0],north=coords[3][0],
                           width_x_m=round(pts[1][0]-pts[0][0],8),height_y_m=round(pts[3][1]-pts[2][1],8)))
    return result


write('Exterior plan spans.csv',exterior(B))
rays=[];sizes=[]
for design,key in [('Original','VGA Map 3'),('Adjusted','VGA Map 1')]:
    obs=[float(r['Isovist Max Radial'])/1000 for r in graphs[key] if float(r['Isovist Max Radial'])>=0]
    rays.append(dict(design=design,input=key+'.csv',locations=len(obs),mean_longest_sightline_m=mean(obs),median_longest_sightline_m=st.median(obs)))
    con=[float(r['Connectivity']) for r in graphs[key]]
    sizes.append(dict(scheme=design,locations=len(con),mean_connectivity=mean(con),mean_visible_fraction=mean(con)/(len(con)-1)))
write('Plan sightline range.csv',rays);write('VGA graph size sensitivity.csv',sizes)
