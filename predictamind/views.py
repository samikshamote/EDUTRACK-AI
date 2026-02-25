from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse

from attendance.models import Attendance, Subject
from django.db.models import Count, Q

from .models import InternalMark

# ================================
# OVERALL ATTENDANCE %
# ================================
def calculate_student_attendance(student):
    records = Attendance.objects.filter(student=student)

    total_classes = records.count()
    present_classes = records.filter(status=True).count()

    if total_classes == 0:
        return 0

    return round((present_classes / total_classes) * 100, 2)


# ================================
# SUBJECT-WISE ATTENDANCE %
# ================================
def subject_wise_attendance(student):
    subjects = Subject.objects.all()
    data = {}

    for subject in subjects:
        records = Attendance.objects.filter(
            student=student,
            subject=subject
        )

        total = records.count()
        present = records.filter(status=True).count()

        if total == 0:
            percentage = 0
        else:
            percentage = round((present / total) * 100, 2)

        data[subject.name] = percentage

    return data


@login_required
def predict_view(request):

    if request.method == "POST":

        student = request.user.student
        attendance_percentage = calculate_student_attendance(student)

        subjects = {
            "Operating System": {
                "internal": float(request.POST.get("os_internal", 0)),
                "assignment": float(request.POST.get("os_assignment", 0)),
            },
            "Web Technology": {
                "internal": float(request.POST.get("wt_internal", 0)),
                "assignment": float(request.POST.get("wt_assignment", 0)),
            },
            "Data Analytics": {
                "internal": float(request.POST.get("da_internal", 0)),
                "assignment": float(request.POST.get("da_assignment", 0)),
            },
            "Java": {
                "internal": float(request.POST.get("java_internal", 0)),
                "assignment": float(request.POST.get("java_assignment", 0)),
            },
        }

        # Calculate subject totals
        totals = {}
        for sub, marks in subjects.items():
            totals[sub] = marks["internal"] + marks["assignment"]

        # Academic Score (average)
        academic_score = sum(totals.values()) / len(totals)

        # Final Score with attendance weight (20%)
        final_score = (academic_score * 0.8) + (attendance_percentage * 0.2)

        status = "PASS" if final_score >= 40 and attendance_percentage >= 50 else "FAIL"

        weak_subject = min(totals, key=totals.get)

        # Smart Timetable
        timetable = {
            weak_subject: "2 hrs daily revision",
            "Other Subjects": "1 hr practice"
        }

        # Personalized AI Advice
        advice = []

        if attendance_percentage < 75:
            advice.append("Your attendance is below 75%. You must attend more lectures.")

        if attendance_percentage < 60:
            advice.append("High academic risk due to low attendance.")

        advice.append(f"You need to improve in {weak_subject}.")
        advice.append("Practice previous year questions.")
        advice.append("Revise concepts weekly.")

        context = {
            "final_score": round(final_score, 2),
            "status": status,
            "timetable": timetable,
            "advice": advice,
            "subjects": totals,
            "inputs": {
                "subjects": subjects,
                "attendance": attendance_percentage
            },
            "attendance_percentage": attendance_percentage,
            "now": now().strftime("%d-%m-%Y")
        }

        request.session["pdf_data"] = context

        return render(request, "predictamind/result.html", context)

    return render(request, "predictamind/predict.html")

@login_required
def generate_pdf(request):

    template = get_template("predictamind/pdf_template.html")
    context = request.session.get("pdf_data")

    if not context:
        return HttpResponse("No data available")

    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Prediction_Report.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response

from attendance.models import Attendance
from .models import InternalMark
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def auto_result(request):

    student = request.user.student

    # =============================
    # 1️⃣ Attendance Calculation
    # =============================

    total_classes = Attendance.objects.filter(student=student).count()
    present_classes = Attendance.objects.filter(student=student, status=True).count()

    attendance_percentage = 0
    if total_classes > 0:
        attendance_percentage = (present_classes / total_classes) * 100

    # =============================
    # 2️⃣ Marks Fetch
    # =============================

    marks = InternalMark.objects.filter(student=student)

    if not marks.exists():
        return render(request, "predictamind/no_marks.html")

    subject_scores = {}
    for m in marks:
        subject_scores[m.subject.name] = m.total()

    academic_average = sum(subject_scores.values()) / len(subject_scores)

    # =============================
    # 3️⃣ Final Weighted Score
    # =============================

    final_score = (academic_average * 0.8) + (attendance_percentage * 0.2)

    # =============================
    # 4️⃣ PASS / FAIL Logic
    # =============================

    if final_score >= 40 and attendance_percentage >= 50:
        result_status = "PASS"
    else:
        result_status = "FAIL"

    # =============================
    # 5️⃣ Weak Subject Detection
    # =============================

    weakest_subject = min(subject_scores, key=subject_scores.get)

    # =============================
    # 6️⃣ AI Advice Generator
    # =============================

    advice = []

    if attendance_percentage < 75:
        advice.append("Your attendance is below 75%. Improve consistency.")

    if attendance_percentage < 60:
        advice.append("Low attendance is affecting academic performance.")

    if final_score >= 75:
        advice.append("Excellent performance. Maintain consistency.")
    elif final_score >= 50:
        advice.append("Good, but improvement required for distinction.")
    else:
        advice.append("High academic risk. Immediate focused study required.")

    advice.append(f"Focus more on {weakest_subject}.")
    advice.append("Follow structured daily study timetable.")

    # =============================
    # 7️⃣ Smart Study Timetable
    # =============================

    study_plan = {}

    for subject, score in subject_scores.items():
        if subject == weakest_subject:
            study_plan[subject] = "2 hours daily"
        else:
            study_plan[subject] = "1 hour daily"

    context = {
        "attendance_percentage": round(attendance_percentage, 2),
        "academic_average": round(academic_average, 2),
        "final_score": round(final_score, 2),
        "status": result_status,
        "subjects": subject_scores,
        "advice": advice,
        "study_plan": study_plan,
    }

    request.session["pdf_data"] = context

    return render(request, "predictamind/auto_result.html", context)
