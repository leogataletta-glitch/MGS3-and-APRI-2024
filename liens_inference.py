"""Restricted wild-cluster bootstrap-t for a binary unadjusted association.

OLS y ~ intercept + z: slope = difference in proportions, H0 slope=0 is
H0 phi=0 for nonconstant binary inputs. CR1 studentization, Rademacher
weights shared within section, all 2**G signs. Enumeration removes Monte
Carlo noise, NOT small-cluster approximation error. No causal inference.
"""
import itertools
from functools import lru_cache
import numpy as np

@lru_cache(maxsize=4)
def signs(g):
    return np.array(list(itertools.product([-1.,1.],repeat=g)))


def section_ids(cat):
    import croisement_moteur as M
    ids=np.full(cat['n'],-1,int);counts=np.zeros(cat['n'],int)
    for j,name in enumerate(M.SECTIONS):
        mask=cat['groupes'].get(name,np.zeros(cat['n'],bool));ids[mask]=j;counts+=mask
    ids[counts!=1]=-1
    return ids


def test(y,z,groups):
    y,z,groups=np.asarray(y,float),np.asarray(z,float),np.asarray(groups)
    out={'p':np.nan,'sections':len(np.unique(groups[groups>=0])),'reason':'sample','phi':np.nan}
    n=len(y)
    if n==0 or len(z)!=n or len(groups)!=n:return out
    if not (np.isin(y,[0,1]).all() and np.isin(z,[0,1]).all()):return out
    a,b=y.sum(),z.sum()
    if min(a,n-a,b,n-b)>0:out['phi']=float((n*(y*z).sum()-a*b)/np.sqrt(a*(n-a)*b*(n-b)))
    if min(a,n-a,b,n-b)<30:return out
    if (groups<0).any():out['reason']='missing_section';return out
    keys=np.unique(groups);g=len(keys)
    if g<8 or g>10:out['reason']='sections';return out
    # Both response levels must have support in several independent sections.
    for v in (y,1-y,z,1-z):
        counts=np.array([v[groups==k].sum() for k in keys])
        if (counts>0).sum()<4 or counts.max()/counts.sum()>.5:
            out['reason']='support';return out
    X=np.column_stack([np.ones(n),z]);inv=np.linalg.inv(X.T@X)
    beta=inv@X.T@y;u=y-X@beta
    A=np.array([X[groups==k].T@X[groups==k] for k in keys])
    scores=np.array([X[groups==k].T@u[groups==k] for k in keys])
    c=g/(g-1)*(n-1)/(n-2);var=c*np.square(scores@inv[:,1]).sum()
    if var<=1e-15:out['reason']='degenerate';return out
    observed=abs(beta[1]/np.sqrt(var))
    # Restricted residuals under H0: constant mean, no association slope.
    u0=y-y.mean();S=np.array([X[groups==k].T@u0[groups==k] for k in keys])
    W=signs(g);delta=(W@S)@inv
    boot_scores=W[:,:,None]*S[None,:,:]-np.einsum('gij,bj->bgi',A,delta)
    boot_var=c*np.square(boot_scores@inv[:,1]).sum(axis=1)
    if (boot_var<=1e-15).any():out['reason']='degenerate';return out
    tstar=np.abs(delta[:,1]/np.sqrt(boot_var))
    out.update(p=float(np.mean(tstar>=observed-1e-10)),reason='ok',draws=len(W))
    return out


def holm(pvalues):
    """All comparisons in the family; untestable entries count as p=1.
    Unavailable results stay unavailable in the returned array.
    """
    p=np.asarray(pvalues,float);valid=np.isfinite(p)
    if ((p[valid]<0)|(p[valid]>1)).any():raise ValueError('p outside [0,1]')
    work=np.where(valid,p,1.);order=np.argsort(work,kind='stable');m=len(p)
    adjusted=np.empty(m);adjusted[order]=np.minimum(1,np.maximum.accumulate(work[order]*(m-np.arange(m))))
    adjusted[~valid]=np.nan
    return adjusted


def family(y,base,masks,sections):
    results=[test(y[base],z[base],sections[base]) for z in masks]
    for r,p in zip(results,holm([r['p'] for r in results])):r['p_holm']=p
    return results
