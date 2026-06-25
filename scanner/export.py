import json
import csv
from typing import List, Dict


def to_json(data: Dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def to_csv(rows: List[Dict], path: str):
    if not rows:
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
        return
    keys = rows[0].keys()
    with open(path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
