from pathlib import Path
import hashlib, json, zipfile, shutil
import pandas as pd

REQUIRED = ["sample_id", "project", "language", "vulnerable_path", "fixed_path",
            "vulnerable_commit", "fixed_commit"]

def read_manifest(uploaded_file):
    df = pd.read_csv(uploaded_file)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError("Manifest is missing required columns: " + ", ".join(missing))
    if df["sample_id"].astype(str).duplicated().any():
        raise ValueError("sample_id values must be unique.")
    return df.fillna("")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def safe_extract_zip(uploaded_file, destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(uploaded_file) as z:
        for info in z.infolist():
            target = (destination / info.filename).resolve()
            if destination not in target.parents and target != destination:
                raise ValueError("Unsafe ZIP path detected; extraction cancelled.")
        z.extractall(destination)
    return destination

def source_inventory(root, extensions=(".js", ".jsx", ".ts", ".tsx")):
    root = Path(root)
    return [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in extensions]
