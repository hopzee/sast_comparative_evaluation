from src.evaluation.metrics import calculate_metrics

def test_metrics_basic():
    m=calculate_metrics(8,2,2,8)
    assert m["Precision"] == 0.8
    assert m["Recall"] == 0.8
    assert round(m["F1"],6) == 0.8
    assert m["FPR"] == 0.2

def test_zero_denominator_is_none():
    m=calculate_metrics(0,0,0,0)
    assert m["Precision"] is None
    assert m["Recall"] is None
    assert m["FPR"] is None

def test_mcc_perfect():
    assert calculate_metrics(5,0,0,5)["MCC"] == 1.0
