"""
Project Title : Student Attendance & Performance Tracker (PS No. 45)
Course        : Programming Fundamentals Using Python (RU-100-05-00058)
Programme     : BCA / First Semester / Section 1C

Description
-----------
Reads student data from a CSV file (Name, Classes_Held, Classes_Attended, Marks),
calculates the attendance percentage of every student, finds the students who are
At Risk and shows the results with a bar chart and a scatter chart.

A student is At Risk if attendance is below 75% OR marks are below 40.
"""

import pandas as pd
import matplotlib.pyplot as plt

COLUMNS = ["Name", "Classes_Held", "Classes_Attended", "Marks"]
MIN_ATTENDANCE = 75    # minimum attendance percentage
MIN_MARKS = 40         # minimum marks (out of 100)


def read_row(row):
    """Validate one CSV row.

    Returns (name, held, attended, marks, None) for a valid row,
    or (None, None, None, None, message) when the row must be skipped.
    """
    name = str(row["Name"]).strip()
    if name == "" or name.lower() == "nan":
        return None, None, None, None, "Name is missing."

    try:
        held = int(float(row["Classes_Held"]))
    except (ValueError, TypeError):
        return None, None, None, None, f"invalid Classes_Held '{row['Classes_Held']}'."

    try:
        attended = int(float(row["Classes_Attended"]))
    except (ValueError, TypeError):
        return None, None, None, None, f"invalid Classes_Attended '{row['Classes_Attended']}'."

    try:
        marks = float(row["Marks"])
    except (ValueError, TypeError):
        return None, None, None, None, f"invalid Marks '{row['Marks']}'."

    if held <= 0:
        return None, None, None, None, "Classes_Held must be greater than 0."
    if attended < 0:
        return None, None, None, None, "Classes_Attended cannot be negative."
    if attended > held:
        return None, None, None, None, f"attended ({attended}) cannot exceed held ({held})."
    if not 0 <= marks <= 100:
        return None, None, None, None, f"Marks {row['Marks']} must be between 0 and 100."

    return name, held, attended, marks, None


def load_data(filename):
    """Load the CSV file with Pandas, clean invalid rows and add the calculated columns.

    Returns None if the file is missing, otherwise a DataFrame (possibly empty).
    """
    try:
        raw = pd.read_csv(filename, header=None, names=COLUMNS, dtype=str,
                          skipinitialspace=True, skip_blank_lines=True)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=COLUMNS)

    # If the file has a header line, drop it
    if len(raw) > 0 and str(raw.iloc[0]["Name"]).strip().lower() == "name":
        raw = raw.iloc[1:]

    valid_rows = []
    for number, (_, row) in enumerate(raw.iterrows(), start=1):
        name, held, attended, marks, error = read_row(row)
        if error:
            print(f"Row {number} skipped: {error}")
        else:
            valid_rows.append([name, held, attended, marks])

    df = pd.DataFrame(valid_rows, columns=COLUMNS)
    if df.empty:
        return df

    # Attendance percentage calculated with Pandas columns
    df["Attendance_Pct"] = df["Classes_Attended"] / df["Classes_Held"] * 100
    return df


def find_at_risk(df):
    """Boolean filtering: students with low attendance OR low marks."""
    return df[(df["Attendance_Pct"] < MIN_ATTENDANCE) | (df["Marks"] < MIN_MARKS)]


def risk_reason(attendance, marks):
    """Return the reason(s) a student is At Risk."""
    reasons = []
    if attendance < MIN_ATTENDANCE:
        reasons.append("attendance below 75%")
    if marks < MIN_MARKS:
        reasons.append("marks below 40")
    return ", ".join(reasons)


def format_marks(marks):
    """Show 80.0 as 80 and keep decimals only when needed."""
    return str(int(marks)) if float(marks).is_integer() else f"{marks:.2f}"


def show_report(df):
    """Menu option 1: attendance %, marks and status of every student."""
    at_risk_names = set(find_at_risk(df)["Name"])
    for _, row in df.iterrows():
        if row["Name"] in at_risk_names:
            status = f"At Risk ({risk_reason(row['Attendance_Pct'], row['Marks'])})"
        else:
            status = "OK"
        print(f"{row['Name']}: {row['Attendance_Pct']:.2f}% │ "
              f"Marks {format_marks(row['Marks'])} │ {status}")


def plot_charts(df):
    """Bar chart (attendance) and scatter chart (attendance vs marks)."""
    at_risk_names = set(find_at_risk(df)["Name"])
    colors = ["tab:red" if name in at_risk_names else "tab:green" for name in df["Name"]]

    # Bar chart
    plt.figure("Attendance Percentage")
    plt.bar(df["Name"], df["Attendance_Pct"], color=colors)
    plt.axhline(MIN_ATTENDANCE, color="black", linestyle="--", label="75% requirement")
    plt.title("Attendance Percentage by Student")
    plt.xlabel("Student")
    plt.ylabel("Attendance (%)")
    plt.ylim(0, 100)
    plt.legend()

    # Scatter chart
    plt.figure("Attendance vs Marks")
    plt.scatter(df["Attendance_Pct"], df["Marks"], c=colors, s=80)
    for _, row in df.iterrows():
        plt.annotate(row["Name"], (row["Attendance_Pct"], row["Marks"]),
                     textcoords="offset points", xytext=(6, 6))
    plt.axvline(MIN_ATTENDANCE, color="gray", linestyle="--")
    plt.axhline(MIN_MARKS, color="gray", linestyle="--")
    plt.title("Attendance vs Marks")
    plt.xlabel("Attendance (%)")
    plt.ylabel("Marks")

    plt.show()


def show_summary(df):
    """Menu option 2: averages, At Risk students and both charts."""
    at_risk = find_at_risk(df)
    names = ", ".join(at_risk["Name"])

    print(f"Average attendance: {df['Attendance_Pct'].mean():.2f}% │ "
          f"Average marks: {df['Marks'].mean():.2f}")
    if len(at_risk) > 0:
        print(f"At Risk students: {len(at_risk)} ({names})")
    else:
        print("At Risk students: 0")
    print("Bar chart and scatter chart 'Attendance vs Marks' displayed")
    plot_charts(df)


def main():
    filename = input("Enter CSV file name (default students.csv): ").strip()
    if filename == "":
        filename = "students.csv"

    df = load_data(filename)
    if df is None:
        return
    if df.empty:
        print("No valid data to analyse.")
        return

    while True:
        print("\n--- Student Attendance & Performance Tracker ---")
        print("1. Report")
        print("2. Summary and charts")
        print("3. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            show_report(df)
        elif choice == "2":
            show_summary(df)
        elif choice == "3":
            print("Thank you. Exiting...")
            break
        else:
            print("Invalid choice. Select 1 to 3.")


if __name__ == "__main__":
    main()