"""
io_ops.py
---------
Import and export features (TXT/JSON/CSV) so data can move in and out
of TimeLoom, as mentioned in the project's block diagram.
"""

import csv
import json
import os


def export_csv(data, filename="timeloom_export.csv"):
    if not data["entries"]:
        print("No entries to export.")
        return

    path = os.path.join(os.path.dirname(__file__), filename)
    fieldnames = ["id", "date", "category", "activity", "start", "end", "duration_minutes", "note"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for e in data["entries"]:
            writer.writerow(e)
    print(f"Exported {len(data['entries'])} entries to {path}")


def export_json(data, filename="timeloom_export.json"):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, "w") as f:
        json.dump(data["entries"], f, indent=2)
    print(f"Exported {len(data['entries'])} entries to {path}")


def import_csv(data, filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    imported = 0
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                entry = {
                    "id": data["next_id"],
                    "date": row.get("date", "-"),
                    "category": row.get("category", "Other"),
                    "activity": row.get("activity", "Imported entry"),
                    "start": row.get("start", "-"),
                    "end": row.get("end", "-"),
                    "duration_minutes": float(row.get("duration_minutes", 0) or 0),
                    "note": row.get("note", "")
                }
                data["entries"].append(entry)
                data["next_id"] += 1
                imported += 1
            except (ValueError, KeyError):
                continue  # skip malformed rows instead of crashing

    print(f"Imported {imported} entries from {filename}.")
    return data
