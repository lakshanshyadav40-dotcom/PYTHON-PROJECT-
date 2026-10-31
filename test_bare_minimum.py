"""Automated Bare Minimum Requirements test for Student Attendance Tracker.
Run: python test_bare_minimum.py
Keep this file in the same folder as student_attendance_tracker.py.
"""
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Run chart tests without opening chart windows.
import matplotlib.pyplot as plt

import one as project

passed = 0
failed = 0


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {label}")
    else:
        failed += 1
        print(f"[FAIL] {label}" + (f" - {detail}" if detail else ""))


print("=" * 62)
print("STUDENT ATTENDANCE TRACKER - BARE MINIMUM REQUIREMENTS TEST")
print("=" * 62)

# 1. Python 3
check("Python 3", sys.version_info.major == 3, sys.version)

# 2. Required libraries
check("Pandas imported", hasattr(pd, "read_csv"))
check("Matplotlib imported", hasattr(plt, "figure"))

# 3. CSV loading and data cleaning
valid_csv = """Name,Classes_Held,Classes_Attended,Marks
Aman,40,36,80
Riya,40,28,65
Karan,40,30,35
Neha,40,30,40
"""
invalid_csv = """Name,Classes_Held,Classes_Attended,Marks
Aman,40,45,80
Riya,40,30,abc
"""

with tempfile.TemporaryDirectory() as temp_dir:
    valid_path = Path(temp_dir) / "valid_students.csv"
    invalid_path = Path(temp_dir) / "invalid_students.csv"
    valid_path.write_text(valid_csv, encoding="utf-8")
    invalid_path.write_text(invalid_csv, encoding="utf-8")

    df = project.load_data(str(valid_path))
    check("CSV loaded into Pandas DataFrame", isinstance(df, pd.DataFrame))
    check("Valid CSV rows loaded", len(df) == 4, f"Rows loaded: {len(df)}")
    check("Attendance percentage calculated", "Attendance_Pct" in df.columns)
    check("Attendance calculation correct", list(df["Attendance_Pct"]) == [90.0, 70.0, 75.0, 75.0])

    # 4. Invalid row cleaning
    with patch("builtins.print") as mocked_print:
        bad_df = project.load_data(str(invalid_path))
    check("Invalid rows skipped", bad_df.empty, f"Rows remaining: {len(bad_df)}")
    printed = " ".join(str(call.args[0]) for call in mocked_print.call_args_list)
    check("Invalid-row reasons reported", "cannot exceed held" in printed and "invalid Marks" in printed)

    # 5. Boolean filtering: attendance < 75 OR marks < 40
    at_risk = project.find_at_risk(df)
    check("Boolean filtering identifies At Risk students",
          set(at_risk["Name"]) == {"Riya", "Karan"},
          f"Found: {list(at_risk['Name'])}")
    check("Boundary values 75% and 40 marks are OK",
          "Neha" not in set(at_risk["Name"]))

    # 6. Average calculations
    check("Average attendance correct", abs(df["Attendance_Pct"].mean() - 77.5) < 0.001)
    check("Average marks correct", abs(df["Marks"].mean() - 55.0) < 0.001)

    # 7-9. Charts and labels; prevent GUI display during automated test.
    plt.close("all")
    with patch.object(plt, "show"):
        project.plot_charts(df)
    figures = [plt.figure(n) for n in plt.get_fignums()]
    titles = [ax.get_title() for fig in figures for ax in fig.axes]
    xlabels = [ax.get_xlabel() for fig in figures for ax in fig.axes]
    ylabels = [ax.get_ylabel() for fig in figures for ax in fig.axes]
    check("Bar chart created", "Attendance Percentage by Student" in titles)
    check("Scatter chart created", "Attendance vs Marks" in titles)
    check("Charts have axis labels",
          "Student" in xlabels and "Attendance (%)" in xlabels and "Marks" in ylabels)
    check("Charts include student annotations",
          any(text.get_text() == "Aman" for fig in figures for ax in fig.axes for text in ax.texts))
    plt.close("all")

print("\n" + "=" * 62)
print(f"RESULT: {passed} PASSED, {failed} FAILED, {passed + failed} TOTAL")
if failed == 0:
    print("BARE MINIMUM REQUIREMENTS: ALL TESTS PASSED")
else:
    print("BARE MINIMUM REQUIREMENTS: CHECK FAILED ITEMS ABOVE")
print("=" * 62)
sys.exit(0 if failed == 0 else 1)
