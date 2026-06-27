"""Extract Spider and BIRD from the local RawDataset zips.

Both datasets are already present locally (no network download):
  - RawDataset/spider_data.zip  -> data/spider/spider_data/
  - RawDataset/bird_data.zip    -> data/bird/dev_20240627/   (full dev, release dev_20240627)
        contains dev.json, dev.sql, dev_tables.json, and a NESTED dev_databases.zip
        which is unpacked to data/bird/dev_20240627/dev_databases/<db>/<db>.sqlite

Usage:
    python scripts/setup_data.py
"""
import zipfile
from pathlib import Path
from text2sql.data.spider import extract_spider

def extract_bird(zip_path: Path, dest: Path) -> Path:
    """Extract bird_data.zip and its nested dev_databases.zip. Returns the dev root."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(dest)
    root = dest / "dev_20240627"
    nested = root / "dev_databases.zip"
    if nested.exists() and not (root / "dev_databases").exists():
        with zipfile.ZipFile(nested) as z:
            z.extractall(root)   # yields root/dev_databases/<db>/<db>.sqlite
    return root

def main():
    spider_zip = Path("RawDataset/spider_data.zip")
    if spider_zip.exists():
        print(f"Spider extracted to {extract_spider(spider_zip, Path('data/spider'))}")
    else:
        print("WARNING: RawDataset/spider_data.zip not found")

    bird_zip = Path("RawDataset/bird_data.zip")
    if bird_zip.exists():
        root = extract_bird(bird_zip, Path("data/bird"))
        dev = root / "dev.json"
        dbs = root / "dev_databases"
        print(f"BIRD extracted to {root} (dev.json={dev.exists()}, dev_databases={dbs.exists()})")
    else:
        print("WARNING: RawDataset/bird_data.zip not found")

if __name__ == "__main__":
    main()
