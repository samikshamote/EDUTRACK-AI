def generate_smart_timetable(subject_totals):
    timetable = {}

    for subject, total in subject_totals.items():
        if total <= 6:
            timetable[subject] = "2 Hours Daily"
        elif total <= 10:
            timetable[subject] = "1 Hour Daily"
        else:
            timetable[subject] = "30 Minutes Revision"

    return timetable


def generate_advice(status, attendance, weak_subjects):

    advice = []

    if attendance < 75:
        advice.append("Improve attendance to at least 75%.")

    if status == "FAIL":
        advice.append("Focus more on weak subjects.")

    if weak_subjects:
        advice.append(f"Weak subjects: {', '.join(weak_subjects)}")

    if not advice:
        advice.append("Keep up the good work!")

    return advice
