"""
storage.py
----------
Handles all reading/writing to the JSON data file.
Keeping this separate from the rest of the app is what makes the
project "modular" - every other file just calls load_data() /
save_data() and never touches the file system directly.
"""

import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

# This is what a brand-new data.json looks like.
DEFAULT_DATA = {
    "categories": ["Study", "Work", "Break", "Exercise", "Other"],
    "entries": [],       # list of finished time-log entries
    "active_timer": None,  # holds a running timer, if any
    "next_id": 1
}


def load_data():
    """Read data.json and return it as a Python dict.
    If the file doesn't exist yet, create it with default values."""
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))  # deep copy

    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        # File got corrupted somehow -> start fresh instead of crashing
        print("Warning: data.json was unreadable. Starting with fresh data.")
        save_data(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))


def save_data(data):
    """Write the given dict back to data.json (pretty-printed)."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
