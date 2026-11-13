import os, json, time, re, requests
from datetime import datetime, timezone

SYSTEM_PROMPT = """You are a cautious source-code security reviewer. Analyze only the supplied source code and context.
Do not assume a vulnerability exists. Do not infer hidden repository facts. Return only JSON matching the requested schema.
A finding requires a specific weakness mechanism and source evidence. If uncertain, state vulnerable=false and explain the limitation.
Do not claim exploitability beyond what the code supports."""

USER_PROMPT_TEMPLATE = """Review the following {language} source code for security vulnerabilities.
Do not use external knowledge about this sample. Do not guess CVEs. Do not claim a vulnerability based only on a broad pattern.
Return JSON with this exact shape:
{{"vulnerable": boolean, "findings": [{{"title": string, "cwe": string, "severity": string,
"file_path": string, "start_line": integer, "end_line": integer, "evidence": string,
"explanation": string, "confidence": number}}], "limitations": string}}
If no supported vulnerability is found, use vulnerable=false and an empty findings array.
Source file: {file_path}
Language: {language}
SOURCE CODE:
```{language}
{source}
```"""

def get_config():
    try:
        import streamlit as st
        key=st.secrets.get("LLM_API_KEY", os.getenv("LLM_API_KEY",""))
        base=st.secrets.get("LLM_BASE_URL", os.getenv("LLM_BASE_URL","https://api.openai.com/v1"))
        model=st.secrets.get("LLM_MODEL", os.getenv("LLM_MODEL",""))
        api_version=st.secrets.get("LLM_API_VERSION", os.getenv("LLM_API_VERSION",""))
    except Exception:
        key=os.getenv("LLM_API_KEY",""); base=os.getenv("LLM_BASE_URL","https://api.openai.com/v1")
        model=os.getenv("LLM_MODEL",""); api_version=os.getenv("LLM_API_VERSION","")
    return {"key":key,"base":base.rstrip("/"),"model":model,"api_version":api_version}

def parse_json_response(text):
    text=text.strip()
    if text.startswith("```"):
        text=re.sub(r"^```(?:json)?\s*","",text)
        text=re.sub(r"\s*```$","",text)
    try: return json.loads(text)
    except json.JSONDecodeError:
        match=re.search(r"\{.*\}",text,re.S)
        if not match: raise ValueError("Model response did not contain valid JSON.")
        return json.loads(match.group(0))

def analyze_source(source, file_path, language, temperature=0, max_tokens=1200, timeout=120):
    cfg=get_config()
    if not cfg["key"] or not cfg["model"]:
        raise RuntimeError("Configure LLM_API_KEY and LLM_MODEL in Streamlit Secrets or environment variables.")
    payload={"model":cfg["model"],"temperature":temperature,"max_tokens":max_tokens,
      "messages":[{"role":"system","content":SYSTEM_PROMPT},
                  {"role":"user","content":USER_PROMPT_TEMPLATE.format(language=language,file_path=file_path,source=source)}]}
    headers={"Authorization":f"Bearer {cfg['key']}","Content-Type":"application/json"}
    started=time.perf_counter()
    response=requests.post(cfg["base"]+"/chat/completions",headers=headers,json=payload,timeout=timeout)
    latency=time.perf_counter()-started
    response.raise_for_status()
    data=response.json()
    content=data["choices"][0]["message"]["content"]
    parsed=parse_json_response(content)
    usage=data.get("usage",{})
    return {"parsed":parsed,"raw_response":data,"latency_seconds":latency,
      "input_tokens":usage.get("prompt_tokens"),"output_tokens":usage.get("completion_tokens"),
      "model":cfg["model"],"api_version":cfg["api_version"],
      "timestamp":datetime.now(timezone.utc).isoformat(),"prompt_version":"sast-review-v1",
      "temperature":temperature,"max_tokens":max_tokens}
