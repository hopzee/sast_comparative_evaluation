import math
from sklearn.metrics import matthews_corrcoef

def calculate_metrics(tp, fp, fn, tn):
    tp,fp,fn,tn=map(int,(tp,fp,fn,tn))
    total=tp+fp+fn+tn
    precision=tp/(tp+fp) if tp+fp else None
    recall=tp/(tp+fn) if tp+fn else None
    f1=(2*precision*recall/(precision+recall)) if precision is not None and recall is not None and precision+recall else (0.0 if precision==0 and recall==0 else None)
    fpr=fp/(fp+tn) if fp+tn else None
    fnr=fn/(fn+tp) if fn+tp else None
    accuracy=(tp+tn)/total if total else None
    try: mcc=matthews_corrcoef([1]*tp+[0]*fp+[1]*fn+[0]*tn,[1]*tp+[1]*fp+[0]*fn+[0]*tn) if total else None
    except Exception: mcc=None
    return {"TP":tp,"FP":fp,"FN":fn,"TN":tn,"N":total,"Precision":precision,"Recall":recall,
      "F1":f1,"FPR":fpr,"FNR":fnr,"Accuracy":accuracy,"MCC":mcc}

def score_instances(samples, findings, ground_truth):
    """One binary outcome per eligible sample; requires explicit negative controls."""
    by_sample={}
    for f in findings:
        sid = str(f.get("sample_id", ""))
        variant = str(f.get("variant", "")).lower()
        # The primary binary outcome is the vulnerable revision. Fixed-revision
        # assessments are retained for a separate vulnerable-vs-fixed analysis.
        if variant == "fixed":
            continue
        if f.get("adjudication") in ("TP", "confirmed"):
            by_sample[sid] = True
    tp=fp=fn=tn=0
    excluded=0
    for s in samples:
        sid=str(s.get("sample_id"))
        gt=ground_truth.get(sid,{})
        status=str(gt.get("ground_truth_status","")).lower()
        eligible=str(gt.get("eligibility",s.get("eligibility",""))).lower()
        if eligible and eligible not in ("eligible","include","yes","true"): 
            excluded+=1; continue
        if status in ("vulnerable","positive","1","true"):
            if by_sample.get(sid): tp+=1
            else: fn+=1
        elif status in ("negative","non_vulnerable","non-vulnerable","0","false"):
            if by_sample.get(sid): fp+=1
            else: tn+=1
        else:
            excluded+=1
    result=calculate_metrics(tp,fp,fn,tn)
    result["Excluded_or_unlabelled"]=excluded
    return result
