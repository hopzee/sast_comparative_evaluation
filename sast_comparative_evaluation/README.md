# SAST Comparative Evaluation Research Application

A Streamlit research workspace for the study **“Comparative Evaluation of AI-Driven and Traditional Static Application Security Testing for Detecting Software Vulnerabilities.”**

## Technology
- Python 3.11
- Streamlit
- Pandas / NumPy
- Semgrep CLI
- CodeQL CLI (optional; requires a separately installed CodeQL CLI and query packs)
- Configurable OpenAI-compatible LLM API
- SciPy / Statsmodels / scikit-learn
- SQLite for local experiment records

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser. Use the sidebar to move through the research workflow.

## Deployment to Streamlit Community Cloud
1. Upload the project files to a GitHub repository. `app.py` must remain at repository root.
2. In Streamlit Community Cloud, create an app from that repository and select `app.py`.
3. Add API credentials only in Streamlit app Secrets (or environment variables in a controlled local environment). Never commit `.env` or `secrets.toml`.
4. Deploy.

### Important deployment limitations
- Streamlit Community Cloud is not a reliable environment for running heavyweight native security scanners. The app detects whether `semgrep` and `codeql` are installed; it does not pretend a scan ran when a binary is missing.
- Recommended workflow: run Semgrep/CodeQL in a controlled local or CI environment, then import genuine Semgrep JSON and CodeQL SARIF reports into this app.
- Streamlit Cloud local disk and SQLite are not durable storage guarantees. Export the experiment records and reports regularly. For long-term multi-user persistence, configure a managed database/object store in a future deployment.
- CodeQL CLI and query packs must be installed and licensed/used according to GitHub's terms and your environment.

## Research protocol implemented
- Primary benchmark: OpenSSF CVE Benchmark, JavaScript/TypeScript only.
- Each eligible case should have documented CVE/CWE evidence, vulnerable and fixed revisions, affected source location, and a recorded eligibility decision.
- OWASP Benchmark is a separate supplementary experiment only; do not merge its Java/Python cases into the primary JS/TS denominator.
- A1 Semgrep, A2 CodeQL, A3 deduplicated traditional union.
- B one fixed LLM model/configuration, standardized prompt, five repeated runs per sample.
- C1 hybrid union, C2 traditional/AI consensus, and evidence-validated findings are separately represented.
- The LLM prompt does not include ground-truth labels, CVE metadata, patch descriptions, expected outcomes, or fix diffs.
- Unlabelled code is not automatically a true negative. True negatives require eligible negative controls.
- A TP requires matching vulnerability mechanism and source evidence, not merely a broad CWE or file-level coincidence.
- Binary vulnerability-instance metrics are kept distinct from finding-level adjudication.
- Statistical comparisons use paired outcomes where appropriate; non-significance is not equivalence.

## Input manifest
CSV upload with at least:
`sample_id, project, language, vulnerable_path, fixed_path, vulnerable_commit, fixed_commit`
Recommended additional fields:
`cve, cwe, repository_url, affected_file, vulnerable_sha256, fixed_sha256, eligibility, ground_truth_status, evidence_note, split`

`vulnerable_path` and `fixed_path` should be paths relative to the extracted source root or absolute paths available to the running environment.

## Scanner imports
- Semgrep: import its native JSON output.
- CodeQL: import SARIF 2.1.0.
- Keep raw reports with your experiment archive and record scanner versions/configuration.

## LLM configuration
Configure `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL` using Streamlit Secrets or environment variables. The adapter expects an OpenAI-compatible `/chat/completions` endpoint. Confirm provider-specific compatibility and terms before use. Record exact model snapshot, API version, parameters, date, token usage, and latency.

## Data and safety
- Uploaded source is treated as untrusted input. Only scan code you are authorized to analyze.
- API keys are never stored in the SQLite research database.
- The app does not execute source files.
- Scanner execution is an optional local feature; imported reports are supported.
- No results are generated until you provide actual data and run/import actual analyses.
