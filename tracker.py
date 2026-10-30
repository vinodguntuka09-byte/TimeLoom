"""
tracker.py
----------
Core operations: starting/stopping the timer, logging entries manually,
editing/deleting entries, managing categories, and searching/filtering.
"""

from datetime import datetime
import storage


DATE_FMT = "%Y-%m-%d"
TIME_FMT = "%H:%M:%S"


def _now_str():
    now = datetime.now()
    return now.strftime(DATE_FMT), now.strftime(TIME_FMT)


# ---------------------------------------------------------------------
# TIMER (start / stop)
# ---------------------------------------------------------------------

def start_timer(data):
    if data["active_timer"] is not None:
        print(f"A timer is already running for '{data['active_timer']['activity']}'. "
              "Stop it before starting a new one.")
        return

    print("\nAvailable categories:", ", ".join(data["categories"]))
    category = input("Category: ").strip() or "Other"
    activity = input("Activity name: ").strip() or "Untitled activity"
    date_str, time_str = _now_str()

    data["active_timer"] = {
        "activity": activity,
        "category": category,
        "date": date_str,
        "start": time_str
    }
    storage.save_data(data)
    print(f"Timer started for '{activity}' at {time_str}.")


def stop_timer(data):
    if data["active_timer"] is None:
        print("No timer is currently running.")
        return

    timer = data["active_timer"]
    _, end_time = _now_str()

    start_dt = datetime.strptime(timer["start"], TIME_FMT)
    end_dt = datetime.strptime(end_time, TIME_FMT)
    duration_minutes = round((end_dt - start_dt).total_seconds() / 60, 2)
    if duration_minutes < 0:
        duration_minutes = 0  # guard against crossing midnight

    entry = {
        "id": data["next_id"],
        "activity": timer["activity"],
        "category": timer["category"],
        "date": timer["date"],
        "start": timer["start"],
        "end": end_time,
        "duration_minutes": duration_minutes,
        "note": ""
    }
    data["entries"].append(entry)
    data["next_id"] += 1
    data["active_timer"] = None
    storage.save_data(data)
    print(f"Timer stopped. Logged {duration_minutes} minutes for '{entry['activity']}'.")


# ---------------------------------------------------------------------
# MANUAL LOGGING (for time already spent, or breaks)
# ---------------------------------------------------------------------

def log_manual_entry(data, is_break=False):
    print("\nAvailable categories:", ", ".join(data["categories"]))
    category = "Break" if is_break else (input("Category: ").strip() or "Other")
    activity = "Break" if is_break else (input("Activity name: ").strip() or "Untitled activity")

    date_str = input(f"Date (YYYY-MM-DD) [default: today]: ").strip()
    if not date_str:
        date_str = datetime.now().strftime(DATE_FMT)

    duration_input = input("Duration in minutes: ").strip()
    try:
        duration_minutes = float(duration_input)
    except ValueError:
        print("Invalid number, entry cancelled.")
        return

    note = input("Note (optional): ").strip()

    entry = {
        "id": data["next_id"],
        "activity": activity,
        "category": category,
        "date": date_str,
        "start": "-",
        "end": "-",
        "duration_minutes": duration_minutes,
        "note": note
    }
    data["entries"].append(entry)
    data["next_id"] += 1
    storage.save_data(data)
    print(f"Logged {duration_minutes} minutes for '{activity}' on {date_str}.")


# ---------------------------------------------------------------------
# EDIT / DELETE
# ---------------------------------------------------------------------

def _find_entry(data, entry_id):
    for entry in data["entries"]:
        if entry["id"] == entry_id:
            return entry
    return None


def edit_entry(data):
    view_timeline(data, silent_if_empty=False)
    try:
        entry_id = int(input("\nEnter the ID of the entry to edit: ").strip())
    except ValueError:
        print("Invalid ID.")
        return

    entry = _find_entry(data, entry_id)
    if entry is None:
        print("Entry not found.")
        return

    print("Leave a field blank to keep it unchanged.")
    new_activity = input(f"Activity [{entry['activity']}]: ").strip()
    new_category = input(f"Category [{entry['category']}]: ").strip()
    new_duration = input(f"Duration in minutes [{entry['duration_minutes']}]: ").strip()
    new_note = input(f"Note [{entry['note']}]: ").strip()

    if new_activity:
        entry["activity"] = new_activity
    if new_category:
        entry["category"] = new_category
    if new_duration:
        try:
            entry["duration_minutes"] = float(new_duration)
        except ValueError:
            print("Invalid duration ignored.")
    if new_note:
        entry["note"] = new_note

    storage.save_data(data)
    print("Entry updated.")


def delete_entry(data):
    view_timeline(data, silent_if_empty=False)
    try:
        entry_id = int(input("\nEnter the ID of the entry to delete: ").strip())
    except ValueError:
        print("Invalid ID.")
        return

    entry = _find_entry(data, entry_id)
    if entry is None:
        print("Entry not found.")
        return

    confirm = input(f"Delete '{entry['activity']}' ({entry['duration_minutes']} min)? (y/n): ").strip().lower()
    if confirm == "y":
        data["entries"].remove(entry)
        storage.save_data(data)
        print("Entry deleted.")
    else:
        print("Cancelled.")


# ---------------------------------------------------------------------
# CATEGORIES
# ---------------------------------------------------------------------

def manage_categories(data):
    while True:
        print("\n--- Manage Categories ---")
        print("Current categories:", ", ".join(data["categories"]))
        print("1. Add category")
        print("2. Remove category")
        print("3. Back to main menu")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            new_cat = input("New category name: ").strip()
            if new_cat and new_cat not in data["categories"]:
                data["categories"].append(new_cat)
                storage.save_data(data)
                print(f"Added category '{new_cat}'.")
            else:
                print("Category is empty or already exists.")
        elif choice == "2":
            cat = input("Category to remove: ").strip()
            if cat in data["categories"]:
                data["categories"].remove(cat)
                storage.save_data(data)
                print(f"Removed category '{cat}'.")
            else:
                print("Category not found.")
        elif choice == "3":
            break
        else:
            print("Invalid option.")


# ---------------------------------------------------------------------
# SEARCH & FILTER / VIEW TIMELINE
# ---------------------------------------------------------------------

def _print_entries(entries):
    if not entries:
        print("No entries found.")
        return
    print(f"{'ID':<4}{'Date':<12}{'Category':<12}{'Activity':<20}{'Start':<10}{'End':<10}{'Min':<8}Note")
    print("-" * 90)
    for e in sorted(entries, key=lambda x: (x["date"], x["start"])):
        print(f"{e['id']:<4}{e['date']:<12}{e['category']:<12}{e['activity'][:18]:<20}"
              f"{e['start']:<10}{e['end']:<10}{e['duration_minutes']:<8}{e['note']}")


def view_timeline(data, silent_if_empty=True):
    if silent_if_empty and not data["entries"]:
        print("No entries logged yet.")
        return
    print("\n--- Timeline (all entries) ---")
    _print_entries(data["entries"])


def search_and_filter(data):
    print("\n--- Search & Filter ---")
    print("1. Filter by category")
    print("2. Filter by date")
    print("3. Search by keyword (activity/note)")
    choice = input("Choose an option: ").strip()

    if choice == "1":
        cat = input("Category: ").strip()
        results = [e for e in data["entries"] if e["category"].lower() == cat.lower()]
    elif choice == "2":
        date_str = input("Date (YYYY-MM-DD): ").strip()
        results = [e for e in data["entries"] if e["date"] == date_str]
    elif choice == "3":
        keyword = input("Keyword: ").strip().lower()
        results = [e for e in data["entries"]
                   if keyword in e["activity"].lower() or keyword in e["note"].lower()]
    else:
        print("Invalid option.")
        return

    _print_entries(results)
