import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
plt.rcParams.update({'font.family':'serif','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
C={'Claude':'#D55E00','Gemini':'#0072B2','GPT':'#009E73'}
# loan
days=[23,22,21,17,16,21,21,19,20,19,23,18,21,23,20,25,26,18,25,19,18,17,22,19,20,19]+[11,12,14,11,13,14,12,11,11,12,14,11,11,11,9,11,9,9,10,9,9,11,11,12,10,8,7,7,8,8,7,8,7,8,9,10]+[7,8,7,7,8,7,8]
seg=[(0,26,'Baseline'),(26,38,'Stage 1'),(38,50,'Stage 2'),(50,62,'Stage 3'),(62,69,'Control')]
fig,ax=plt.subplots(figsize=(6.5,2.8)); x=np.arange(69)
ax.plot(x,days,'o',ms=3,color='0.55')
for a,b,l in seg:
    m=np.mean(days[a:b]); ax.hlines(m,a-0.4,b-0.6,color='#0072B2',lw=2)
    ax.text((a+b-1)/2,4.0,f'{l}\n$\\bar{{x}}$ = {m:.1f}',ha='center',va='top',fontsize=7.5)
for i,l in [(26,'Int. 1 (Dec 2021)'),(38,'Int. 2 (Dec 2022)'),(50,'Int. 3 (Dec 2023)')]:
    ax.axvline(i-0.5,ls='--',color='0.4',lw=0.8); ax.text(i,27,l,fontsize=7.5,va='top')
ax.set_ylim(5,28); ax.set_xlim(-1,69); ax.set_xticks([]); ax.set_ylabel('Days to disburse')
fig.tight_layout(); fig.subplots_adjust(bottom=0.2); fig.savefig('figures/loan_staircase.pdf')
# cusum
S={'Claude':[0.477,0.287,0.097,0,0],'Gemini':[0.143,0,0.143,0.287,0.430],'GPT':[0,0,0.143,0,0]}
fig,ax=plt.subplots(figsize=(5.2,2.6)); r=np.arange(1,6)
for m,v in S.items(): ax.plot(r,v,'-o',ms=4,color=C[m],label=m)
ax.axhline(0.67,ls='--',color='0.3',lw=1); ax.text(5.08,0.67,'$h=0.67$',va='center',fontsize=8)
ax.axhline(0.40,ls=':',color='0.3',lw=1); ax.text(5.08,0.40,'$h=0.40$',va='center',fontsize=8)
ax.set_xticks(r,[f'Run {i}' for i in r]); ax.set_ylabel('$S_t$'); ax.set_ylim(-0.03,0.8); ax.set_xlim(0.8,5.6)
ax.legend(frameon=False,fontsize=8,loc='upper center',ncol=3)
fig.tight_layout(); fig.savefig('figures/cusum.pdf')
# ewma
Z={'Claude':[81.33,85.07,86.72,89.38,91.50],'Gemini':[86.67,89.33,86.13,82.24,79.13],'GPT':[92.00,93.60,89.55,91.64,93.31]}
L=[82.52,80.42,79.29,78.62,78.21]
fig,ax=plt.subplots(figsize=(5.2,2.8))
for m,v in Z.items(): ax.plot(r,v,'-o',ms=4,color=C[m],label=m)
ax.plot(r,L,'--',color='0.3',lw=1,label='$\\mathrm{LCL}_t$')
ax.axhline(90,ls=':',color='0.5',lw=0.8); ax.text(0.85,90.3,'$\\mu_0=90$',fontsize=8)
ax.plot(1,81.33,'o',ms=11,mfc='none',mec='#CC0000',mew=1.5); ax.annotate('signal',(1,81.33),(1.25,79.0),fontsize=8,color='#CC0000')
ax.set_xticks(r,[f'Run {i}' for i in r]); ax.set_ylabel('$z_t$ (EWMA of LPRI)'); ax.set_ylim(76,96)
ax.legend(frameon=False,fontsize=8,loc='upper center',ncol=4)
fig.tight_layout(); fig.savefig('figures/ewma.pdf')
