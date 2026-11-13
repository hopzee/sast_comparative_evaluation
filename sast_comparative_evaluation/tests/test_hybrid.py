from src.hybrid.build import build_hybrid

def test_hybrid_keeps_disagreement_and_consensus():
    rows=[
      {"tool":"Semgrep","sample_id":"S1","file_path":"a.js","start_line":10,"end_line":12,"cwe":"CWE-79","evidence":"sink"},
      {"tool":"LLM","sample_id":"S1","file_path":"a.js","start_line":11,"end_line":12,"cwe":"CWE-79","evidence":"sink"},
      {"tool":"CodeQL","sample_id":"S2","file_path":"b.js","start_line":4,"end_line":4,"cwe":"CWE-89","evidence":"query"}
    ]
    result=build_hybrid(rows)
    assert len(result["union"]) == 2
    assert len(result["consensus"]) == 1
    assert len(result["evidence_candidates"]) == 2
