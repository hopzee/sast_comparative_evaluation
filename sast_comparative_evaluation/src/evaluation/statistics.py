import numpy as np
from scipy.stats import wilcoxon
from statsmodels.stats.contingency_tables import mcnemar

def mcnemar_test(a, b):
    a=np.asarray(a,dtype=bool); b=np.asarray(b,dtype=bool)
    if len(a)!=len(b) or len(a)==0: return {"status":"Not run: paired vectors must have equal non-zero length."}
    both=int(np.sum((a==1)&(b==1))); a_only=int(np.sum((a==1)&(b==0)))
    b_only=int(np.sum((a==0)&(b==1))); neither=int(np.sum((a==0)&(b==0)))
    table=[[both,a_only],[b_only,neither]]
    result=mcnemar(table,exact=(a_only+b_only)<25,correction=True)
    return {"n_pairs":len(a),"both_detected":both,"a_only":a_only,"b_only":b_only,
      "neither":neither,"statistic":float(result.statistic),"p_value":float(result.pvalue)}

def wilcoxon_test(a,b):
    a=np.asarray(a,dtype=float); b=np.asarray(b,dtype=float)
    if len(a)!=len(b) or len(a)==0: return {"status":"Not run: paired vectors must have equal non-zero length."}
    try:
        stat,p=wilcoxon(a,b,zero_method="wilcox")
        return {"n_pairs":len(a),"statistic":float(stat),"p_value":float(p)}
    except Exception as e: return {"status":str(e)}

def bootstrap_mean_ci(values, n_boot=2000, confidence=.95, seed=17):
    x=np.asarray(values,dtype=float)
    if len(x)==0: return {"estimate":None,"lower":None,"upper":None,"n":0}
    rng=np.random.default_rng(seed)
    means=np.array([rng.choice(x,size=len(x),replace=True).mean() for _ in range(n_boot)])
    alpha=1-confidence
    return {"estimate":float(x.mean()),"lower":float(np.quantile(means,alpha/2)),
            "upper":float(np.quantile(means,1-alpha/2)),"n":len(x)}


def holm_adjust(p_values):
    """Holm-Bonferroni adjusted p-values, preserving input order."""
    p = np.asarray(p_values, dtype=float)
    if np.any((p < 0) | (p > 1)):
        raise ValueError("p-values must be between 0 and 1")
    m = len(p)
    order = np.argsort(p)
    adjusted = np.empty(m, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p[idx])
        adjusted[idx] = min(1.0, running)
    return adjusted.tolist()

def cluster_bootstrap_mean_ci(values, clusters, n_boot=2000, confidence=.95, seed=17):
    """Bootstrap whole project/vulnerability clusters, not individual rows."""
    x = np.asarray(values, dtype=float)
    c = np.asarray(clusters, dtype=object)
    if len(x) != len(c):
        raise ValueError("values and clusters must have equal length")
    unique = np.unique(c)
    if len(unique) == 0:
        return {"estimate": None, "lower": None, "upper": None, "n_clusters": 0}
    groups = [x[c == label] for label in unique]
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(n_boot):
        chosen = rng.integers(0, len(groups), size=len(groups))
        draw = np.concatenate([groups[i] for i in chosen])
        means.append(draw.mean())
    alpha = 1 - confidence
    return {"estimate": float(x.mean()), "lower": float(np.quantile(means, alpha/2)),
            "upper": float(np.quantile(means, 1-alpha/2)), "n_clusters": int(len(unique))}
