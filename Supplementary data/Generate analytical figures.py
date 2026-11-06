from pathlib import Path
import csv, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle
B=Path(__file__).resolve().parent
F=B.parent/'Figures'; F.mkdir(exist_ok=True)
G=B
A=json.loads((B/'Figure input summaries.json').read_text(encoding='utf-8'))
plt.rcParams.update({'font.family':'Times New Roman','font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
def save(fig,name):
    fig.savefig(F/(name+'.png'),dpi=350,bbox_inches='tight',pad_inches=.08)
    fig.savefig(F/(name+'.svg'),bbox_inches='tight',pad_inches=.08)
    plt.close(fig)
# Explicit phase and actor sequence. The feedback arrow denotes manual design review.
fig,ax=plt.subplots(figsize=(8.2,3.1));ax.set_xlim(0,10);ax.set_ylim(0,3);ax.axis('off')
texts=[('1  Use feedback','Management, staff and visitors\nCirculation, scale and viewing'),('2  Model and edit','Design team\nUnity / C# interactive review'),('3  Configuration analysis','Researcher\nSeparate Depthmap analysis'),('4  Evaluate the alternative','15 students + 15 stakeholders\nScheme and tool feedback')]
for i,(head,body) in enumerate(texts):
 x=.03+i*2.52;ax.add_patch(Rectangle((x,1.1),2.36,1.35,facecolor='#f0f3f5',edgecolor='#56626a',linewidth=.8))
 ax.text(x+.12,2.2,head,weight='bold',fontsize=9);ax.text(x+.12,1.75,body,fontsize=8,va='top',linespacing=1.6)
 if i<3:ax.annotate('',xy=(x+2.51,1.77),xytext=(x+2.36,1.77),arrowprops=dict(arrowstyle='->',color='#384752',lw=1))
ax.annotate('',xy=(3.72,1.08),xytext=(6.25,1.08),arrowprops=dict(arrowstyle='->',connectionstyle='bar,fraction=-.23',lw=.9))
ax.text(5,.36,'Manual interpretation and further design revision',ha='center',fontsize=8)
ax.text(5,.02,'One project-level alternative precedes participant evaluation',ha='center',fontsize=9)
save(fig,'Figure 1 Workflow')

# Read the original ASCII DXF without changing the model.
cad=B/'Technical sources/Drawing1.dxf'
ll=cad.read_text(errors='replace').splitlines();pairs=[(int(k.strip()),v.strip()) for k,v in zip(ll[::2],ll[1::2])]
st=next(i for i,x in enumerate(pairs) if x==(2,'ENTITIES'));en=next(i for i in range(st,len(pairs)) if pairs[i]==(0,'ENDSEC'))
entities=[];e=[]
for code,val in pairs[st+1:en]:
 if code==0:
  if e:entities.append(e)
  e=[(code,val)]
 else:e.append((code,val))
if e:entities.append(e)
lines=[]
for e in entities:
 typ=e[0][1];v={k:s for k,s in e};layer=v.get(8,'')
 if any(k in layer.upper() for k in ['DIM','TEXT']):continue
 def f(k,default=0):return float(v.get(k,default))
 if typ=='LINE':lines.append(((f(10),f(20)),(f(11),f(21))))
 elif typ=='LWPOLYLINE':
  verts=[]
  for k,s in e:
   if k==10:verts.append([float(s),0,0])
   elif k==20 and verts:verts[-1][1]=float(s)
   elif k==42 and verts:verts[-1][2]=float(s)
  if int(v.get(70,'0'))&1 and verts:verts.append(verts[0])
  for p,q in zip(verts,verts[1:]):
   if abs(p[2])<1e-10:lines.append((p[:2],q[:2]));continue
   p0=np.array(p[:2]);p1=np.array(q[:2]);dv=p1-p0;ch=np.linalg.norm(dv)
   if ch==0:continue
   theta=4*np.arctan(p[2]);mid=(p0+p1)/2;normal=np.array([-dv[1],dv[0]])/ch
   center=mid+normal*ch*(1-p[2]**2)/(4*p[2]);rad=np.linalg.norm(p0-center);angle=np.arctan2(*(p0-center)[::-1]);ts=np.linspace(angle,angle+theta,20)
   pts=center+rad*np.column_stack((np.cos(ts),np.sin(ts)));lines.extend(zip(pts[:-1],pts[1:]))
 elif typ=='ARC':
  a0=f(50);a1=f(51)
  if a1<a0:a1+=360
  ts=np.radians(np.linspace(a0,a1,30));pts=np.column_stack((f(10)+f(40)*np.cos(ts),f(20)+f(40)*np.sin(ts)));lines.extend(zip(pts[:-1],pts[1:]))
 elif typ=='ELLIPSE':
  ts=np.linspace(f(41),f(42,2*np.pi),50);major=np.array([f(11),f(21)]);minor=np.array([-major[1],major[0]])*f(40,1);pts=np.array([f(10),f(20)])+np.cos(ts)[:,None]*major+np.sin(ts)[:,None]*minor;lines.extend(zip(pts[:-1],pts[1:]))
lines=np.array(lines)/1000
maps=[]
for name in ['VGA Map 3','VGA Map 1']:
 with (G/(name+'.csv')).open() as ff:rows=list(csv.DictReader(ff))
 key=np.array([int(r['key']) for r in rows]);x=(key>>16)*.6-130.8;y=(key&65535)*.6-1.2
 maps.append(dict(name=name,rows=rows,x=x,y=y,xmin=x.min(),ymin=y.min()))
fig,axs=plt.subplots(1,2,figsize=(8.2,4.2))
for ax,m,label in zip(axs,maps,['(a) Original plan representation','(b) Adjusted plan representation']):
 x,y=m['x'],m['y'];bbox=(x.min()-3,x.max()+3,y.min()-3,y.max()+3)
 use=lines[(lines[:,:,0].mean(axis=1)>bbox[0])&(lines[:,:,0].mean(axis=1)<bbox[1])&(lines[:,:,1].mean(axis=1)>bbox[2])&(lines[:,:,1].mean(axis=1)<bbox[3])].copy()
 use[:,:,0]-=m['xmin'];use[:,:,1]-=m['ymin'];ax.add_collection(LineCollection(use,colors='#263746',linewidths=.35))
 ax.scatter(x-m['xmin'],y-m['ymin'],c='#9bb9cc',marker='s',s=1,alpha=.35,linewidths=0)
 ax.set(xlim=(-4,69),ylim=(-5,70),aspect='equal');ax.set_title(label,loc='left',fontsize=9);ax.axis('off')
 ax.plot([2,22],[-2,-2],color='black',lw=1.2);ax.text(12,-4,'20 m',ha='center',fontsize=8)
save(fig,'Figure 4 Plan comparison')

# Identical colour scales within each metric; coordinate frame aligned only for display.
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'path'})
fig,axs=plt.subplots(2,2,figsize=(8.2,8.0),layout='constrained')
for row,(col,title) in enumerate([('Visual Integration [HH]','Visual integration HH'),('Visual Mean Depth','Visual mean depth')]):
 vals=[np.array([float(r[col]) for r in m['rows']]) for m in maps];lo=min(a.min() for a in vals);hi=max(a.max() for a in vals)
 for j,(m,a) in enumerate(zip(maps,vals)):
  ax=axs[row,j];x=m['x']-m['xmin'];y=m['y']-m['ymin'];xx=np.rint(x/.6).astype(int);yy=np.rint(y/.6).astype(int);arr=np.full((max(yy)+1,max(xx)+1),np.nan);arr[yy,xx]=a
  im=ax.imshow(arr,origin='lower',extent=(-.3,max(x)+.3,-.3,max(y)+.3),cmap='turbo',vmin=lo,vmax=hi,interpolation='none')
  ax.set(xlim=(-2,68),ylim=(-2,69),aspect='equal');ax.axis('off');ax.set_title(f"({'abcd'[row*2+j]}) {'Original' if j==0 else 'Adjusted'} | {title}",fontsize=9,loc='left')
  ax.plot([2,22],[0,0],color='black',lw=1);ax.text(12,-1.8,'20 m',fontsize=7,ha='center')
 cb=fig.colorbar(im,ax=axs[row,:],shrink=.75,pad=.01);cb.ax.tick_params(labelsize=8)
save(fig,'Figure 7 Visibility analysis')
plt.rcParams.update({'font.family':'Times New Roman','font.size':10,'svg.fonttype':'none'})

fig,axs=plt.subplots(2,2,figsize=(8.2,5.7),layout='constrained')
for j,(name,title) in enumerate([('zx2','Original'),('zx1','Adjusted')]):
 with (G/(name+'.csv')).open() as f:rows=list(csv.DictReader(f))
 for i,(label,col) in enumerate([('Intelligibility','Connectivity'),('Synergy','Integration [HH] R3')]):
  a=np.array([(float(r[col]),float(r['Integration [HH]'])) for r in rows if float(r[col])>=0 and float(r['Integration [HH]'])>=0]);ax=axs[i,j]
  fit=np.polyfit(a[:,0],a[:,1],1);r2=np.corrcoef(a[:,0],a[:,1])[0,1]**2
  ax.scatter(*a.T,s=16,color='#335c81',alpha=.8);xs=np.array([0,12]) if i==0 else np.array([0,3.1]);ax.plot(xs,np.polyval(fit,xs),c='#b87c4c',lw=1)
  ax.set(xlabel='Connectivity' if i==0 else 'Local integration HH (R3)',ylabel='Global integration HH',xlim=(0,12) if i==0 else (0,3.1),ylim=(.4,2.8));ax.set_title(f"({'abcd'[i*2+j]}) {title} | {label}",loc='left',fontsize=9)
  ax.text(.04,.93,f'n = {len(a)}; R² = {r2:.3f}',transform=ax.transAxes,va='top',fontsize=8);ax.grid(alpha=.15)
save(fig,'Figure 8 Axial correlations')

colors=['#f2f2f2','#cccccc','#999999','#666666','#222222']
labels={'Circulation':'Q10  Circulation','Display':'Q11  Display function','Distinctiveness':'Q12  Spatial distinctiveness','Comfort':'Q13  Spatial comfort','Function':'Q14  Functional requirements','Satisfaction':'Q15  Overall satisfaction','VRInterface':'Q16  Interface ease','Discomfort':'Q17  Physical discomfort','SpatialUnderstand':'Q18  Spatial understanding support','IterationEfficiency':'Q19  Perceived iteration efficiency','CreativeFreedom':'Q20  Creative freedom'}
for keys,num,title in [(['Circulation','Display','Distinctiveness','Comfort','Function','Satisfaction'],9,'Adjusted scheme'),(['VRInterface','Discomfort','SpatialUnderstand','IterationEfficiency','CreativeFreedom'],10,'Tool experience')]:
 fig,ax=plt.subplots(figsize=(8.2,3.1));data=[next(x for x in A['questionnaire'] if x['var']==k) for k in keys];ys=np.arange(len(keys));left=np.zeros(len(keys))
 for i,c in enumerate(colors):
  v=np.array([d['student']['counts'][i] for d in data]);ax.barh(ys,v,left=left,color=c,height=.66,edgecolor='#555555',linewidth=.5,label=str(i+1))
  for j,nn in enumerate(v):
   if nn:ax.text(left[j]+nn/2,j,str(nn),ha='center',va='center',fontsize=8,color='white' if i in [3,4] else 'black')
  left+=v
 for j,d in enumerate(data):ax.text(left[j]+.25,j,'n = '+str(d['student']['n']),fontsize=8,va='center')
 ax.set_yticks(ys,[labels[k] for k in keys]);ax.invert_yaxis();ax.set(xlim=(0,16),xlabel='Number of legible student ratings');ax.set_xticks([0,2,4,6,8,10,12,14]);ax.legend(title='Score',ncol=5,loc='lower center',bbox_to_anchor=(.5,1.0),frameon=False,handlelength=1.4);ax.spines[['left','right','top']].set_visible(False);ax.tick_params(axis='y',length=0)
 fig.tight_layout();save(fig,f'Figure {num} {title}')


# Retain the final compact workflow layout.
fig=plt.figure(figsize=(8.2,2.55));ax=fig.add_axes([.01,.01,.98,.98]);ax.set_xlim(0,10);ax.set_ylim(0,3);ax.axis('off')
cards=[('1  Use feedback','Management, staff\nand visitors\nCirculation, scale, viewing'),('2  Model and edit','Design team\nInteractive Unity model\nController transformations'),('3  Analyse configuration','Researcher\nSeparate Depthmap analysis\nOriginal / adjusted states'),('4  Evaluate alternative','15 students +\n15 project stakeholders\nScheme and tool feedback')]
for i,(head,body) in enumerate(cards):
 x=.02+i*2.52;ax.add_patch(Rectangle((x,1.00),2.35,1.8,fc='#f0f3f5',ec='#56626a',lw=.8))
 ax.text(x+.10,2.55,head,fontsize=9.3,weight='bold',va='top');ax.text(x+.10,2.07,body,fontsize=8.5,va='top',linespacing=1.6)
 if i<3:ax.annotate('',(x+2.50,1.80),(x+2.35,1.80),arrowprops=dict(arrowstyle='->',lw=1))
ax.annotate('',(3.72,.99),(6.25,.99),arrowprops=dict(arrowstyle='->',connectionstyle='bar,fraction=-.16',lw=.9))
ax.text(5,.32,'Manual interpretation and further design revision',ha='center',fontsize=8.5)
ax.text(5,.03,'One project-level alternative precedes participant evaluation',ha='center',fontsize=9)
save(fig,'Figure 1 Workflow')
