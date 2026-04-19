"""Grade computation logic for studykit."""

LETTER_GRADES = [
    (93, "A"), (90, "A-"), (87, "B+"), (83, "B"), (80, "B-"),
    (77, "C+"), (73, "C"), (70, "C-"), (67, "D+"), (63, "D"),
    (60, "D-"), (0, "F"),
]

GRADE_POINTS = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0,
    "D-": 0.7, "F": 0.0,
}


def pct(score, max_score):
    """Return percentage score."""
    if max_score == 0:
        return 0.0
    return (score / max_score) * 100.0


def letter_grade(percentage):
    """Convert a percentage to a letter grade."""
    for threshold, letter in LETTER_GRADES:
        if percentage >= threshold:
            return letter
    return "F"


def course_average(grades, course):
    """
    Compute weighted average percentage for a given course.

    Returns None if no grades exist for that course.
    """
    course_grades = [g for g in grades if g["course"].lower() == course.lower()]
    if not course_grades:
        return None

    total_weight = sum(g["weight"] for g in course_grades)
    if total_weight == 0:
        return None

    weighted_sum = sum(pct(g["score"], g["max_score"]) * g["weight"] for g in course_grades)
    return weighted_sum / total_weight


def compute_gpa(grades, courses):
    """
    Compute credit-weighted GPA across all courses.

    Returns None if no courses have grades.
    """
    total_credits = 0
    total_points = 0.0

    for course in courses:
        avg = course_average(grades, course["name"])
        if avg is None:
            continue
        letter = letter_grade(avg)
        points = GRADE_POINTS.get(letter, 0.0)
        credits = course.get("credits", 3)
        total_credits += credits
        total_points += points * credits

    if total_credits == 0:
        return None

    return total_points / total_credits


def predict_needed(grades, course, target_pct, remaining_weight):
    """
    Predict what score is needed on remaining_weight of work to hit target_pct overall.

    Formula: needed = (target * total_weight - current_weighted_sum) / remaining_weight
    Returns None if calculation is not possible.
    """
    course_grades = [g for g in grades if g["course"].lower() == course.lower()]

    current_weighted_sum = sum(pct(g["score"], g["max_score"]) * g["weight"] for g in course_grades)
    current_weight = sum(g["weight"] for g in course_grades)
    total_weight = current_weight + remaining_weight

    if remaining_weight <= 0:
        return None

    needed = (target_pct * total_weight - current_weighted_sum) / remaining_weight
    return needed
