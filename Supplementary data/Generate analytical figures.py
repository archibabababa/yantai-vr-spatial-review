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
plt.rcParams.update({'font.family':'Times New Roman','font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
def save(fig,name):
    fig.savefig(F/(name+'.png'),dpi=350,bbox_inches='tight',pad_inches=.08)
    fig.savefig(F/(name+'.svg'),bbox_inches='tight',pad_inches=.08)
    plt.close(fig)

# Figure 1. Revision proceeds in sequence; evidence comes back through two parallel comparisons.
fig = plt.figure(figsize=(6.30, 3.46))
ax = fig.add_axes([0, 0, 1, 1])
ax.set(xlim=(0, 6.30), ylim=(0, 3.46))
ax.axis('off')

def heading(x, y, label):
    ax.text(x, y, label, va='top', ha='left', fontsize=12, weight='bold')

def action(x, y, actor, description):
    ax.text(x, y, actor, va='top', ha='left', fontsize=10.2, weight='bold')
    ax.text(x, y - .22, description, va='top', ha='left',
            fontsize=9.9, linespacing=1.14)

def direction(x1, x2, y):
    ax.annotate('', xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='-|>', color='black', lw=.8,
                                mutation_scale=8, shrinkA=0, shrinkB=0))

heading(.07, 3.40, 'Development of the alternative')
ax.plot([.07, 6.23], [3.11, 3.11], color='black', lw=.85)
action(.07, 3.01, 'Building stakeholders',
       'Report problems with routes,\nscale and viewing distance.')
action(2.21, 3.01, 'Research team',
       'Encode linked movements of\nthree volumes in the VR tool.')
action(4.40, 3.01, 'Design team',
       'Edit the volumes in VR and\nretain one revised layout.')
direction(1.67, 2.04, 2.94)
direction(3.65, 4.19, 2.94)

heading(.07, 2.09, 'Evaluation of the original and adjusted layouts')
ax.plot([.07, 6.23], [1.80, 1.80], color='black', lw=.85)
ax.plot([3.10, 3.10], [.91, 1.73], color='.65', lw=.55)
action(.07, 1.69, 'Plan comparison',
       'Researchers redraw the adjusted plan in CAD\nand compare the two layouts in Depthmap.')
action(3.24, 1.69, 'Participant assessment',
       'Both groups review drawings and video clips\nof the original layout, then explore and rate\nthe adjusted proposal in VR.')

# Join the geometric and participant evidence at the single interpretation step.
ax.plot([1.5, 1.5, 4.75, 4.75], [.87, .76, .76, .87], color='.28', lw=.75)
ax.annotate('', xy=(3.13, .56), xytext=(3.13, .76),
            arrowprops=dict(arrowstyle='-|>', color='.18', lw=.75,
                            mutation_scale=8, shrinkA=0, shrinkB=0))
ax.add_patch(Rectangle((.07, .03), 6.16, .51, fc='.94', ec='none'))
ax.text(3.15, .405, 'Research team', fontsize=10.3, weight='bold', va='center', ha='center')
ax.text(3.15, .195, 'Interpret changes in the plan alongside participant ratings and comments.',
        fontsize=9.9, va='center', ha='center')
save(fig, 'Figure 1 Workflow')
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


# Figure 4. Derive symbols from corresponding stair treads in the two CAD plans.
segments={dict(e)[5]:np.array([[float(dict(e)[10]),float(dict(e)[20])],
                               [float(dict(e)[11]),float(dict(e)[21])]])/1000.
          for e in entities if e[0][1]=='LINE'}
def local_segment(handle,m):
    return segments[handle]-np.array([m['xmin'],m['ymin']])
def tread_run_centre(handles,m):
    return np.mean([local_segment(h,m).mean(axis=0) for h in handles],axis=0)
def corresponding_anteroom(point):
    # Reference tread on the same upper volume: opposite endpoint order, if any, is normalised.
    segments_by_plan=[]
    for h,m in zip(['18CE','1647'],maps):
        line=local_segment(h,m)
        segments_by_plan.append(line[np.argsort(line[:,0])])
    orig,adj=segments_by_plan
    a=complex(*(adj[1]-adj[0]));o=complex(*(orig[1]-orig[0]))
    p=complex(*orig[0]) + (complex(*point)-complex(*adj[0]))*o/a
    return np.array([p.real,p.imag])
adjusted_review=np.array([28.4,41.3])
positions=[]
for i,m in enumerate(maps):
    flight=[['1AC3','1AF9'],['1491','1B87']][i]
    broad=[['18CE','18D5'],['1647','164D']][i]
    positions.append([corresponding_anteroom(adjusted_review) if i==0 else adjusted_review,
                      tread_run_centre(flight,m),tread_run_centre(broad,m)])

fig = plt.figure(figsize=(6.30, 4.10))
axes = [fig.add_axes([.012, .267, .478, .700]), fig.add_axes([.511, .267, .478, .700])]
panel_titles = ['(a) Original plan', '(b) Adjusted plan']

for index, (ax, m, title) in enumerate(zip(axes, maps, panel_titles)):
    x, y = m['x'], m['y']
    bounds = (x.min()-3, x.max()+3, y.min()-3, y.max()+3)
    centres = lines.mean(axis=1)
    chosen = lines[(centres[:, 0] > bounds[0]) & (centres[:, 0] < bounds[1]) &
                   (centres[:, 1] > bounds[2]) & (centres[:, 1] < bounds[3])].copy()
    chosen -= np.array([m['xmin'], m['ymin']])
    ax.add_collection(LineCollection(chosen, colors='#263746', linewidths=.31))
    ax.scatter(x-m['xmin'], y-m['ymin'], color='#9bb9cc', marker='s',
               s=.72, alpha=.35, linewidths=0)
    ax.set(xlim=(-4,69), ylim=(-5,68), aspect='equal')
    ax.axis('off')
    ax.set_title(title, loc='left', fontsize=10.5, pad=2)
    ax.plot([2,22],[-2,-2], color='black', lw=1.05)
    ax.text(12, -3.25, '20 m', va='top', ha='center', fontsize=8.8)
    for j,(xm,ym) in enumerate(positions[index],1):
        ax.scatter([xm],[ym],marker='o',s=56,facecolor='black',
                   edgecolor='white',linewidths=.65,zorder=6)
        ax.annotate(str(j),xy=(xm,ym),xytext=(0,0),textcoords='offset points',va='center',ha='center',
                    color='white',weight='bold',fontsize=7.1,zorder=7)

# Figure 4 reports whole-map attributes at positions close to each numbered landmark.
with (G / 'Landmark visibility.csv').open(encoding='utf-8-sig', newline='') as f:
    central = {(r['design'], int(r['marker'])): r for r in csv.DictReader(f)
               if float(r['radius_m']) == 1.2}
panel = fig.add_axes([.025, .005, .95, .228])
panel.set(xlim=(0, 1), ylim=(0, 1))
panel.axis('off')
panel.text(.008, .90, 'Landmark', weight='bold', fontsize=9.8)
panel.text(.556, .90, 'Longest sightline (m)', ha='center', weight='bold', fontsize=9.8)
panel.text(.875, .90, 'Visual clustering', ha='center', weight='bold', fontsize=9.8)
panel.plot([0, 1], [.78, .78], color='.27', lw=.65)
for marker, (label, y) in enumerate(zip(
        ['Anteroom review area', 'Ascending approach stair', 'Triangular broad steps'],
        [.61, .35, .09]), 1):
    panel.scatter([.021], [y], s=68, color='black')
    panel.text(.021, y, str(marker), ha='center', va='center', color='white', weight='bold', fontsize=7.3)
    panel.text(.048, y, label, va='center', fontsize=9.4)
    original, adjusted = (central[d, marker] for d in ('Original', 'Adjusted'))
    for x, key, places in [(.556, 'median_longest_sightline_m', 1),
                           (.875, 'median_visual_clustering', 3)]:
        pair = [format(float(row[key]), f'.{places}f') for row in (original, adjusted)]
        panel.text(x, y, ' → '.join(pair), ha='center', va='center', fontsize=9.5)
save(fig, 'Figure 4 Plan comparison')


# Identical colour scales within each metric; coordinate frame aligned only for display.
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'path'})
fig=plt.figure(figsize=(8.6,8.35))
grid=fig.add_gridspec(2,3,width_ratios=[1,1,.045],left=.025,right=.935,bottom=.045,top=.955,wspace=.20,hspace=.26)
axs=np.array([[fig.add_subplot(grid[i,j]) for j in range(2)] for i in range(2)])
for row,(col,title) in enumerate([('Visual Integration [HH]','Visual integration HH'),('Visual Mean Depth','Visual mean depth')]):
 vals=[np.array([float(r[col]) for r in m['rows']]) for m in maps];lo=min(a.min() for a in vals);hi=max(a.max() for a in vals)
 for j,(m,a) in enumerate(zip(maps,vals)):
  ax=axs[row,j];x=m['x']-m['xmin'];y=m['y']-m['ymin'];xx=np.rint(x/.6).astype(int);yy=np.rint(y/.6).astype(int);arr=np.full((max(yy)+1,max(xx)+1),np.nan);arr[yy,xx]=a
  im=ax.imshow(arr,origin='lower',extent=(-.3,max(x)+.3,-.3,max(y)+.3),cmap='turbo',vmin=lo,vmax=hi,interpolation='none')
  ax.set(xlim=(-2,68),ylim=(-6,69),aspect='equal');ax.axis('off');ax.set_title(f"({'abcd'[row*2+j]}) {'Original' if j==0 else 'Adjusted'} | {title}",fontsize=9,loc='left')
  ax.plot([2,22],[-2.0,-2.0],color='black',lw=1);ax.text(12,-4.7,'20 m',fontsize=8,ha='center')
 cax=fig.add_subplot(grid[row,2])
 pos=cax.get_position();cax.set_position([pos.x0,pos.y0+pos.height*.13,pos.width,pos.height*.74])
 cb=fig.colorbar(im,cax=cax);cb.ax.tick_params(labelsize=8)
save(fig,'Figure 7 Visibility analysis')
plt.rcParams.update({'font.family':'Times New Roman','font.size':10,'svg.fonttype':'none'})

fig,axs=plt.subplots(2,2,figsize=(8.2,5.7),layout='constrained')
for j,(name,title) in enumerate([('zx2','Original'),('zx1','Adjusted')]):
 with (G/(name+'.csv')).open() as f:rows=list(csv.DictReader(f))
 for i,(label,col) in enumerate([('Intelligibility','Connectivity'),('Synergy','Integration [HH] R3')]):
  a=np.array([(float(r[col]),float(r['Integration [HH]'])) for r in rows if float(r[col])>=0 and float(r['Integration [HH]'])>=0]);ax=axs[i,j]
  fit=np.polyfit(a[:,0],a[:,1],1);r2=np.corrcoef(a[:,0],a[:,1])[0,1]**2
  ax.scatter(*a.T,s=18,facecolors='#cccccc',edgecolors='#282828',linewidths=.55,zorder=3);xs=np.array([0,12]) if i==0 else np.array([0,3.1]);ax.plot(xs,np.polyval(fit,xs),c='#151515',lw=1.15,ls='--',zorder=2)
  ax.set(xlabel='Connectivity' if i==0 else 'Local integration HH (R3)',ylabel='Global integration HH',xlim=(0,12) if i==0 else (0,3.1),ylim=(.4,2.8));ax.set_title(f"({'abcd'[i*2+j]}) {title} | {label}",loc='left',fontsize=9)
  ax.text(.04,.93,f'n = {len(a)}; R² = {r2:.3f}',transform=ax.transAxes,va='top',fontsize=8);ax.grid(alpha=.15)
save(fig,'Figure 8 Axial correlations')

# Figures 9 and 10. Each cell is a count on the recorded response scale.
import runpy
_, rating_rows = runpy.run_path(str(B/'Compare presence and score spread.py'))['calculate'](B)
grid_data = {(r['group'], r['variable']): r for r in rating_rows}
presence_items = [('Drawings_Presence','Drawings · original'),('Video_Presence','Video clips · original'),
                  ('VRSpace_Presence','VR · revised'),('Reference_Presence','Group reference*')]
scheme_items = [('Circulation','Q10   Circulation'),('Display','Q11   Display function'),
                ('Distinctiveness','Q12   Spatial distinctiveness'),('Comfort','Q13   Spatial comfort'),
                ('Function','Q14   Functional fit'),('Satisfaction','Q15   Overall satisfaction'),
                ('VRInterface','Q16   Interface ease'),('Discomfort','Q17   Physical discomfort'),
                ('SpatialUnderstand','Q18   Spatial understanding'),('IterationEfficiency','Q19   Iteration efficiency'),
                ('CreativeFreedom','Q20   Creative freedom')]
keys = ['score_'+str(i) for i in range(1,6)] + ['interval_1_2','interval_4_5','unresolved']
headers = ['1','2','3','4','5','1–2','4–5','?']
for number, title, entries in [(9,'Presence by representation',presence_items),(10,'Scheme and tool ratings',scheme_items)]:
    h = 1.38 + .305*len(entries)
    fig = plt.figure(figsize=(9.4,h))
    ax = fig.add_axes([.015,.04,.978,.935])
    ax.set_xlim(0,25.2);ax.set_ylim(len(entries)+.70,-2.15);ax.axis('off')
    cuts = [3] if number==9 else [6]
    for left, group, heading in [(6.5,'Students','Architecture students (15)'),(16.1,'Experts','Architectural experts (15)')]:
        ax.text(left+4.0,-1.80,heading,ha='center',va='center',fontsize=12.4,weight='bold')
        ax.plot([left,left+8],[-1.37,-1.37],color='.24',lw=.65)
        for j,txt in enumerate(headers):
            ax.text(left+j+.5,-.75,txt,ha='center',va='center',fontsize=10.5)
        for i,(var, label) in enumerate(entries):
            y=i+.18
            if group=='Students':
                ax.text(.08,y,label,ha='left',va='center',fontsize=11)
            for j,key in enumerate(keys):
                count=grid_data[group,var][key]
                shade = 1 - .80*(count/15)
                ax.add_patch(Rectangle((left+j,y-.43),1,.87,facecolor=str(shade),edgecolor='.86',lw=.38))
                ax.text(left+j+.5,y,str(count),ha='center',va='center',fontsize=10.3,
                        color='white' if shade<.52 else '.48' if count==0 else '.08')
        ax.plot([left+5,left+5],[-.36,len(entries)-.38],lw=.82,color='.4')
    for cut in cuts:
        ax.plot([.08,24.1],[cut-.33,cut-.33],color='.45',lw=.6)
    ax.text(.08,-.75,'Representation' if number==9 else 'Questionnaire item',fontsize=11.3,weight='bold',va='center')
    ax.text(.08,len(entries)+.36,'Each row totals 15 per group.   1–2 and 4–5 = interval responses.   ? = unscorable response.',
            fontsize=9.6,ha='left',va='center')
    save(fig, f'Figure {number} {title}')
