"""
Student Result Analyzer
-----------------------
Run program : python student_result_analyzer.py
Run tests   : python student_result_analyzer.py --test

Workflow: Input -> Validation -> Processing -> Report -> CSV save
"""

import csv
import sys
import unittest
from statistics import mean

PASS_MARK = 40


# ---------------- Validation ----------------
class ValidationError(ValueError):
    """Raised when user input is invalid."""


def validate_name(name):
    name = name.strip()
    if not name:
        raise ValidationError("Name cannot be empty.")
    if not all(ch.isalpha() or ch.isspace() for ch in name):
        raise ValidationError("Name must contain only letters and spaces.")
    return name.title()


def validate_marks(value, max_marks=100):
    try:
        marks = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"'{value}' is not a valid number.")
    if not 0 <= marks <= max_marks:
        raise ValidationError(f"Marks must be between 0 and {max_marks}.")
    return marks


def validate_positive_int(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"'{value}' is not a valid whole number.")
    if number <= 0:
        raise ValidationError("Number must be greater than 0.")
    return number


# ---------------- Data processing ----------------
def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    if percentage >= 80:
        return "A"
    if percentage >= 70:
        return "B"
    if percentage >= 60:
        return "C"
    if percentage >= PASS_MARK:
        return "D"
    return "F"


def analyze_student(name, subjects):
    """subjects = {subject_name: marks}"""
    if not subjects:
        raise ValueError("At least one subject is required.")
    total = sum(subjects.values())
    percentage = total / len(subjects)
    passed = all(m >= PASS_MARK for m in subjects.values())
    return {
        "name": name,
        "subjects": subjects,
        "total": round(total, 2),
        "percentage": round(percentage, 2),
        "grade": calculate_grade(percentage),
        "status": "PASS" if passed else "FAIL",
    }


def class_statistics(results):
    if not results:
        raise ValueError("No student results available.")
    percentages = [r["percentage"] for r in results]
    topper = max(results, key=lambda r: r["percentage"])
    passed = sum(1 for r in results if r["status"] == "PASS")
    return {
        "students": len(results),
        "average": round(mean(percentages), 2),
        "highest": max(percentages),
        "lowest": min(percentages),
        "topper": topper["name"],
        "pass_percentage": round(passed / len(results) * 100, 2),
    }


def save_to_csv(results, filename="results.csv"):
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Total", "Percentage", "Grade", "Status"])
            for r in results:
                writer.writerow([r["name"], r["total"], r["percentage"],
                                 r["grade"], r["status"]])
    except OSError as err:
        raise OSError(f"Could not save file '{filename}': {err}")


# ---------------- User interface ----------------
def ask(prompt, validator):
    """Keep asking until the input passes validation."""
    while True:
        try:
            return validator(input(prompt))
        except ValidationError as err:
            print(f"  Invalid input: {err}")


def read_student():
    name = ask("Student name: ", validate_name)
    count = ask("Number of subjects: ", validate_positive_int)
    subjects = {}
    for i in range(1, count + 1):
        subject = input(f"  Subject {i} name: ").strip() or f"Subject {i}"
        subjects[subject] = ask(f"  Marks in {subject} (0-100): ", validate_marks)
    return analyze_student(name, subjects)


def print_report(results):
    print("\n" + "=" * 52)
    print(f"{'Name':<18}{'Total':>8}{'%':>8}{'Grade':>7}{'Status':>9}")
    print("-" * 52)
    for r in results:
        print(f"{r['name']:<18}{r['total']:>8}{r['percentage']:>8}"
              f"{r['grade']:>7}{r['status']:>9}")
    print("=" * 52)
    s = class_statistics(results)
    print(f"Students: {s['students']} | Average: {s['average']}%")
    print(f"Highest: {s['highest']}% | Lowest: {s['lowest']}%")
    print(f"Topper: {s['topper']} | Pass rate: {s['pass_percentage']}%")


def main():
    print("=== Student Result Analyzer ===")
    results = []
    try:
        while True:
            results.append(read_student())
            if input("Add another student? (y/n): ").strip().lower() != "y":
                break
    except (KeyboardInterrupt, EOFError):
        print("\nInput interrupted.")

    if not results:
        print("No data entered.")
        return

    print_report(results)
    try:
        save_to_csv(results)
        print("\nResults saved to results.csv")
    except OSError as err:
        print(f"\nWarning: {err}")


# ---------------- Tests ----------------
class TestValidators(unittest.TestCase):
    def test_valid_name(self):
        self.assertEqual(validate_name("  sachin m "), "Sachin M")

    def test_invalid_name(self):
        for bad in ("abc123", "   "):
            with self.assertRaises(ValidationError):
                validate_name(bad)

    def test_marks(self):
        self.assertEqual(validate_marks("85.5"), 85.5)
        for bad in ("abc", "-1", "101", ""):
            with self.assertRaises(ValidationError):
                validate_marks(bad)

    def test_positive_int(self):
        self.assertEqual(validate_positive_int("3"), 3)
        for bad in ("0", "-2", "x", "2.5"):
            with self.assertRaises(ValidationError):
                validate_positive_int(bad)


class TestAnalyzer(unittest.TestCase):
    def test_grades(self):
        self.assertEqual(calculate_grade(95), "A+")
        self.assertEqual(calculate_grade(75), "B")
        self.assertEqual(calculate_grade(40), "D")
        self.assertEqual(calculate_grade(39.9), "F")

    def test_analyze_student(self):
        r = analyze_student("Ravi", {"Math": 80, "Sci": 70, "Eng": 90})
        self.assertEqual(r["total"], 240)
        self.assertEqual(r["percentage"], 80)
        self.assertEqual(r["grade"], "A")
        self.assertEqual(r["status"], "PASS")

    def test_fail_on_one_subject(self):
        self.assertEqual(analyze_student("Amit", {"M": 30, "S": 90})["status"], "FAIL")

    def test_empty_subjects(self):
        with self.assertRaises(ValueError):
            analyze_student("X", {})

    def test_class_stats(self):
        s = class_statistics([analyze_student("A", {"M": 90}),
                              analyze_student("B", {"M": 50})])
        self.assertEqual(s["average"], 70)
        self.assertEqual(s["topper"], "A")
        self.assertEqual(s["pass_percentage"], 100)

    def test_stats_empty(self):
        with self.assertRaises(ValueError):
            class_statistics([])


if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.argv.remove("--test")
        unittest.main(verbosity=2)
    else:
        main()