"""
main.py
-------
TimeLoom - Productivity Visualizer
Entry point: shows the menu and routes the user's choice to the
right function in tracker.py / analytics.py / io_ops.py.

Run with:  python3 main.py
"""

import storage
import tracker
import analytics
import io_ops


MENU = """
==========================================
   TimeLoom - Productivity Visualizer
==========================================
 1. Start Timer
 2. Stop Timer
 3. Log Time Manually
 4. Log a Break
 5. Edit Entry
 6. Delete Entry
 7. Manage Categories
 8. Search & Filter
 9. View Timeline
10. Reports & Analytics (summary + heatmap)
11. Export Data (CSV/JSON)
12. Import Data (CSV)
13. Exit
==========================================
"""


def main():
    data = storage.load_data()

    while True:
        print(MENU)
        choice = input("Choose an option (1-13): ").strip()

        if choice == "1":
            tracker.start_timer(data)
        elif choice == "2":
            tracker.stop_timer(data)
        elif choice == "3":
            tracker.log_manual_entry(data)
        elif choice == "4":
            tracker.log_manual_entry(data, is_break=True)
        elif choice == "5":
            tracker.edit_entry(data)
        elif choice == "6":
            tracker.delete_entry(data)
        elif choice == "7":
            tracker.manage_categories(data)
        elif choice == "8":
            tracker.search_and_filter(data)
        elif choice == "9":
            tracker.view_timeline(data)
        elif choice == "10":
            analytics.full_report(data)
        elif choice == "11":
            fmt = input("Export as (csv/json): ").strip().lower()
            if fmt == "json":
                io_ops.export_json(data)
            else:
                io_ops.export_csv(data)
        elif choice == "12":
            filename = input("CSV filename to import (must be in the timeloom folder): ").strip()
            io_ops.import_csv(data, filename)
            storage.save_data(data)
        elif choice == "13":
            print("Goodbye! Keep tracking your time with TimeLoom.")
            break
        else:
            print("Invalid choice, please enter a number from 1-13.")


if __name__ == "__main__":
    main()
