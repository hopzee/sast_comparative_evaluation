def _same(a, b):
    if str(a.get("sample_id", "")) != str(b.get("sample_id", "")):
        return False
    path_a = str(a.get("file_path", "")).replace("\\", "/")
    path_b = str(b.get("file_path", "")).replace("\\", "/")
    if path_a != path_b:
        return False
    variant_a = str(a.get("variant", "")).lower()
    variant_b = str(b.get("variant", "")).lower()
    if variant_a and variant_b and variant_a != variant_b:
        return False
    try:
        a1 = int(a.get("start_line") or 0)
        a2 = int(a.get("end_line") or a1)
        b1 = int(b.get("start_line") or 0)
        b2 = int(b.get("end_line") or b1)
        overlap = bool(a1 and b1 and max(a1, b1) <= min(max(a1, a2), max(b1, b2)))
    except (TypeError, ValueError):
        overlap = False
    cwe_a = str(a.get("cwe", "")).lower().strip()
    cwe_b = str(b.get("cwe", "")).lower().strip()
    return overlap and (not cwe_a or not cwe_b or cwe_a == cwe_b)


def build_hybrid(findings):
    traditional = [f for f in findings if f.get("tool") in ("Semgrep", "CodeQL")]
    ai = [f for f in findings if f.get("tool") == "LLM"]
    union = []
    for finding in traditional + ai:
        match = next((item for item in union if _same(item, finding)), None)
        if match is None:
            item = dict(finding)
            item["hybrid_members"] = [finding.get("tool")]
            item["hybrid_status"] = "union"
            union.append(item)
        else:
            match["hybrid_members"] = sorted(set(match.get("hybrid_members", []) + [finding.get("tool")]))
    consensus = []
    for finding in union:
        if len(set(finding.get("hybrid_members", []))) >= 2:
            item = dict(finding)
            item["hybrid_status"] = "consensus"
            consensus.append(item)
    evidence_candidates = []
    for finding in union:
        try:
            has_line = int(finding.get("start_line") or 0) > 0
        except (TypeError, ValueError):
            has_line = False
        if finding.get("evidence") and finding.get("file_path") and has_line:
            item = dict(finding)
            item["hybrid_status"] = "evidence_candidate"
            evidence_candidates.append(item)
    return {"union": union, "consensus": consensus, "evidence_candidates": evidence_candidates}
