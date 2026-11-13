from src.data.schema import normalize_finding

def test_normalize():
    f=normalize_finding({"path":"src/a.js","line":7,"message":"possible issue"},"Semgrep","X1")
    assert f["sample_id"]=="X1"
    assert f["file_path"]=="src/a.js"
    assert f["start_line"]==7
