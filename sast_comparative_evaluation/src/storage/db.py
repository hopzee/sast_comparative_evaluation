import sqlite3
from pathlib import Path
import json
from datetime import datetime, timezone

DB_PATH = Path("data/research.sqlite3")

def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS samples (
          sample_id TEXT PRIMARY KEY, payload TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS ground_truth (
          sample_id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS findings (
          finding_id TEXT PRIMARY KEY, tool TEXT NOT NULL, sample_id TEXT,
          payload TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS runs (
          run_id TEXT PRIMARY KEY, sample_id TEXT, tool TEXT NOT NULL,
          payload TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS adjudications (
          finding_id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS settings (
          key TEXT PRIMARY KEY, value TEXT NOT NULL
        );
        """)
        c.commit()

def _now():
    return datetime.now(timezone.utc).isoformat()

def upsert_sample(sample_id, payload):
    with _connect() as c:
        c.execute("INSERT OR REPLACE INTO samples VALUES (?,?,?)",
                  (str(sample_id), json.dumps(payload, default=str), _now()))

def get_samples():
    with _connect() as c:
        return [json.loads(r["payload"]) for r in c.execute("SELECT payload FROM samples ORDER BY sample_id")]

def upsert_ground_truth(sample_id, payload):
    with _connect() as c:
        c.execute("INSERT OR REPLACE INTO ground_truth VALUES (?,?,?)",
                  (str(sample_id), json.dumps(payload, default=str), _now()))

def get_ground_truth():
    with _connect() as c:
        return {r["sample_id"]: json.loads(r["payload"]) for r in c.execute("SELECT * FROM ground_truth")}

def add_finding(finding_id, tool, sample_id, payload):
    with _connect() as c:
        c.execute("INSERT OR REPLACE INTO findings VALUES (?,?,?,?,?)",
                  (finding_id, tool, sample_id, json.dumps(payload, default=str), _now()))

def get_findings(tool=None):
    with _connect() as c:
        if tool:
            rows = c.execute("SELECT payload FROM findings WHERE tool=? ORDER BY created_at", (tool,))
        else:
            rows = c.execute("SELECT payload FROM findings ORDER BY created_at")
        return [json.loads(r["payload"]) for r in rows]

def clear_findings(tool=None):
    with _connect() as c:
        if tool:
            c.execute("DELETE FROM findings WHERE tool=?", (tool,))
        else:
            c.execute("DELETE FROM findings")

def add_run(run_id, sample_id, tool, payload):
    with _connect() as c:
        c.execute("INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?)",
                  (run_id, sample_id, tool, json.dumps(payload, default=str), _now()))

def get_runs(tool=None):
    with _connect() as c:
        if tool:
            rows = c.execute("SELECT payload FROM runs WHERE tool=? ORDER BY created_at", (tool,))
        else:
            rows = c.execute("SELECT payload FROM runs ORDER BY created_at")
        return [json.loads(r["payload"]) for r in rows]

def save_adjudication(finding_id, payload):
    with _connect() as c:
        c.execute("INSERT OR REPLACE INTO adjudications VALUES (?,?,?)",
                  (finding_id, json.dumps(payload, default=str), _now()))

def get_adjudications():
    with _connect() as c:
        return {r["finding_id"]: json.loads(r["payload"]) for r in c.execute("SELECT * FROM adjudications")}

def export_all():
    return {
      "samples": get_samples(), "ground_truth": get_ground_truth(),
      "findings": get_findings(), "runs": get_runs(),
      "adjudications": get_adjudications()
    }
