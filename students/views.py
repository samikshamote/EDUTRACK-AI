from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q

from attendance.models import Attendance, Timetable, Subject
from teachers.models import InternalMarks
from students.models import Student
from .forms import StudentProfileForm, StudentRegistrationForm


# =====================================================
# STUDENT DASHBOARD
# =====================================================
@login_required
def dashboard(request):
    # Block teachers from accessing student dashboard
    if not hasattr(request.user, 'student'):
        return redirect('teacher_dashboard')

    student = request.user.student

    total = Attendance.objects.filter(student=student).count()
    present = Attendance.objects.filter(student=student, status=True).count()
    percentage = (present / total * 100) if total > 0 else 0

    context = {
        'total': total,
        'present': present,
        'percentage': round(percentage, 2)
    }

    return render(request, 'students/dashboard.html', context)


# =====================================================
# VIEW PROFILE
# =====================================================
@login_required
def student_profile(request):
    if not hasattr(request.user, 'student'):
        return redirect('teacher_dashboard')

    student = request.user.student

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully ✅")
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=student)

    return render(request, 'students/profile.html', {
        'student': student,
        'form': form
    })


# =====================================================
# EDIT PROFILE
# =====================================================
@login_required
def edit_student_profile(request):
    if not hasattr(request.user, 'student'):
        return redirect('teacher_dashboard')

    student = request.user.student

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully ✅")
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=student)

    return render(request, 'students/edit_profile.html', {'form': form})


# =====================================================
# STUDENT REGISTRATION
# =====================================================
def student_register(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists ❌")
                return redirect('student_register')

            # Create inactive user (needs approval)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.is_active = False
            user.save()

            student = form.save(commit=False)
            student.user = user
            student.is_approved = False
            student.save()

            messages.success(
                request,
                "Registration submitted. Wait for teacher approval."
            )
            return redirect('login')

    else:
        form = StudentRegistrationForm()

    return render(request, 'students/register.html', {'form': form})


# =====================================================
# STUDENT RESULTS
# =====================================================
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth

@login_required
def student_results(request):
    if not hasattr(request.user, 'student'):
        return redirect('teacher_dashboard')

    student = request.user.student
    semester = student.semester

    subjects = Subject.objects.filter(semester=semester)
    subject_data = []

    total_internal = 0
    total_subjects = subjects.count()

    weak_subjects = []

    for subject in subjects:

        # =============================
        # ATTENDANCE CALCULATION
        # =============================
        total_classes = Attendance.objects.filter(
            student=student,
            subject=subject
        ).count()

        present_classes = Attendance.objects.filter(
            student=student,
            subject=subject,
            status=True
        ).count()

        attendance_percentage = (
            (present_classes / total_classes) * 100
            if total_classes > 0 else 0
        )

        # =============================
        # INTERNAL MARKS
        # =============================
        mark_obj = InternalMarks.objects.filter(
            student=student,
            subject=subject
        ).first()

        internal_marks = mark_obj.marks if mark_obj else 0
        total_internal += internal_marks

        pass_status = "PASS" if internal_marks >= 6 else "FAIL"

        if internal_marks < 6:
            weak_subjects.append(subject.name)

        # =============================
        # FINAL SCORE (simple formula)
        # =============================
        final_score = round(
            (attendance_percentage * 0.2) + (internal_marks * 5),
            2
        )

        subject_data.append({
            "subject": subject.name,
            "attendance": round(attendance_percentage, 2),
            "internal": internal_marks,
            "status": pass_status,
            "final_score": final_score
        })

    # =============================
    # OVERALL PERFORMANCE
    # =============================
    overall_percentage = (
        (total_internal / (total_subjects * 15)) * 100
        if total_subjects > 0 else 0
    )

    # =============================
    # MONTHLY ATTENDANCE
    # =============================
    monthly_records = (
        Attendance.objects
        .filter(student=student)
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(
            total=Count("id"),
            present=Count("id", filter=Q(status=True))
        )
        .order_by("month")
    )

    monthly_data = []
    for m in monthly_records:
        percent = (m["present"] / m["total"]) * 100 if m["total"] > 0 else 0
        monthly_data.append({
            "month": m["month"].strftime("%B"),
            "percentage": round(percent, 2)
        })

    # =============================
    # AI ADVICE
    # =============================
    if overall_percentage >= 75:
        advice = "Excellent performance. Maintain consistency."
    elif overall_percentage >= 50:
        advice = "Good performance. Focus more on weak subjects."
    else:
        advice = "Performance is low. Increase study time and attendance."

    # =============================
    # AI STUDY PLAN
    # =============================
    study_plan = []
    for weak in weak_subjects:
        study_plan.append(f"Spend 1 extra hour daily on {weak}")

    if not study_plan:
        study_plan.append("Maintain current study routine.")

    context = {
        "subjects": subject_data,
        "overall_percentage": round(overall_percentage, 2),
        "monthly_data": monthly_data,
        "advice": advice,
        "study_plan": study_plan
    }

    return render(request, "students/results.html", context)

# =====================================================
# MANUAL RESULT GENERATOR (Student Self Calculation)
# =====================================================
# =====================================================
# PREDICT RESULT
# =====================================================
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import io
import matplotlib.pyplot as plt
import base64

@login_required
def predict_result(request):
    if not hasattr(request.user, 'student'):
        return redirect('teacher_dashboard')

    results = []
    total = 0
    percentage = 0
    grade = ""
    status = ""

    if request.method == "POST":
        subjects = request.POST.getlist('subject')
        marks = request.POST.getlist('marks')

        valid_subjects = 0
        chart_labels = []
        chart_marks = []

        for subject, mark in zip(subjects, marks):
            if subject.strip() != "" and mark.strip() != "":
                try:
                    mark = int(mark)
                except:
                    mark = 0

                total += mark
                valid_subjects += 1

                chart_labels.append(subject)
                chart_marks.append(mark)

                results.append({
                    "subject": subject,
                    "marks": mark
                })

        if valid_subjects > 0:
            percentage = round((total / (valid_subjects * 100)) * 100, 2)

        # Grade logic
        if percentage >= 90:
            grade = "A"
        elif percentage >= 75:
            grade = "B"
        elif percentage >= 50:
            grade = "C"
        else:
            grade = "Fail"

        status = "PASS" if percentage >= 50 else "FAIL"

        # Chart generation
        plt.figure(figsize=(6,4))
        plt.bar(chart_labels, chart_marks)
        plt.title("Marks Chart")
        plt.xlabel("Subjects")
        plt.ylabel("Marks")

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        chart = base64.b64encode(image_png).decode('utf-8')
        buffer.close()
        plt.close()

        return render(request, 'students/predict.html', {
            "results": results,
            "total": total,
            "percentage": percentage,
            "grade": grade,
            "status": status,
            "chart": chart
        })

    return render(request, 'students/predict.html')

# =====================================================
# STUDENT TIMETABLE
# =====================================================
@login_required
def student_timetable(request):
    if not hasattr(request.user, 'student'):
        return redirect('teacher_dashboard')

    student = request.user.student

    timetable = Timetable.objects.all()

    timetable_slots = timetable.values_list(
        'start_time', 'end_time'
    ).distinct().order_by('start_time')

    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    return render(request, 'students/timetable.html', {
        'timetable': timetable,
        'timetable_slots': timetable_slots,
        'days': days
    })


# =====================================================
# STUDENT ATTENDANCE
# =====================================================
@login_required
def student_attendance(request):
    if not hasattr(request.user, 'student'):
        return redirect('teacher_dashboard')

    student = request.user.student
    records = Attendance.objects.filter(student=student)

    return render(request, 'students/student_attendance.html', {
        'records': records
    })


# =====================================================
# STUDENT REGISTRATION
# =====================================================
def student_register(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists ❌")
                return redirect('student_register')

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.is_active = False
            user.save()

            student = form.save(commit=False)
            student.user = user
            student.is_approved = False
            student.save()

            messages.success(
                request,
                "Registration submitted. Wait for teacher approval."
            )
            return redirect('login')

    else:
        form = StudentRegistrationForm()

    return render(request, 'students/register.html', {'form': form})


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from django.http import HttpResponse
from django.utils.timezone import now
from django.conf import settings
import io
import os

@login_required
def download_result_pdf(request):

    if not hasattr(request.user, 'student'):
        return redirect('teacher_dashboard')

    student = request.user.student
    semester = student.semester
    subjects = Subject.objects.filter(semester=semester)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # =====================================
    # WATERMARK FUNCTION
    # =====================================
    def add_watermark(canvas_obj, doc):
        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica", 60)
        canvas_obj.setFillColorRGB(0.92, 0.92, 0.92)
        canvas_obj.drawCentredString(300, 400, "ACADEMIC PORTAL")
        canvas_obj.restoreState()

    # =====================================
    # COLLEGE LOGO
    # =====================================
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'kaveri_logo.png')

    if os.path.exists(logo_path):
        logo = Image(logo_path, 1.3 * inch, 1.3 * inch)
        elements.append(logo)

    elements.append(Spacer(1, 0.2 * inch))

    # =====================================
    # UNIVERSITY HEADER
    # =====================================
    elements.append(Paragraph("<b>OFFICIAL UNIVERSITY MARKSHEET</b>", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"<b>Student Name:</b> {request.user.username}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Semester:</b> {semester}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Date Generated:</b> {now().strftime('%d %B %Y')}", styles["Normal"]))
    elements.append(Spacer(1, 0.4 * inch))

    # =====================================
    # SUBJECT TABLE
    # =====================================
    table_data = [["Subject", "Attendance %", "Internal", "Final Score"]]

    grand_total = 0
    total_internal = 0
    subject_count = subjects.count()

    for subject in subjects:

        total_classes = Attendance.objects.filter(
            student=student, subject=subject
        ).count()

        present_classes = Attendance.objects.filter(
            student=student, subject=subject, status=True
        ).count()

        attendance_percentage = (
            (present_classes / total_classes) * 100
            if total_classes > 0 else 0
        )

        mark_obj = InternalMarks.objects.filter(
            student=student, subject=subject
        ).first()

        internal_marks = mark_obj.marks if mark_obj else 0
        total_internal += internal_marks

        final_score = round(
            (attendance_percentage * 0.2) + (internal_marks * 5), 2
        )

        grand_total += final_score

        table_data.append([
            subject.name,
            f"{round(attendance_percentage,2)}%",
            internal_marks,
            final_score
        ])

    table = Table(table_data, colWidths=[2.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.8, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.4 * inch))

    # =====================================
    # OVERALL CALCULATION
    # =====================================
    overall_percentage = (
        (total_internal / (subject_count * 15)) * 100
        if subject_count > 0 else 0
    )

    # Grade Logic
    if overall_percentage >= 90:
        grade = "A+"
        badge = "🏆 Outstanding Performer"
    elif overall_percentage >= 75:
        grade = "A"
        badge = "🎖 Excellent Performance"
    elif overall_percentage >= 60:
        grade = "B"
        badge = "👍 Good Performance"
    elif overall_percentage >= 50:
        grade = "C"
        badge = "Satisfactory"
    else:
        grade = "F"
        badge = "Needs Improvement"

    # AI Advice
    if overall_percentage >= 75:
        advice = "Excellent academic performance. Maintain consistency."
    elif overall_percentage >= 50:
        advice = "Good performance. Focus more on weaker subjects."
    else:
        advice = "Performance is low. Increase study time and attendance."

    # =====================================
    # SUMMARY SECTION
    # =====================================
    elements.append(Paragraph(f"<b>Grand Total Score:</b> {round(grand_total,2)}", styles["Heading3"]))
    elements.append(Paragraph(f"<b>Overall Percentage:</b> {round(overall_percentage,2)}%", styles["Heading3"]))
    elements.append(Paragraph(f"<b>Grade:</b> {grade}", styles["Heading3"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"<b>Performance Badge:</b> {badge}", styles["Heading3"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("<b>AI Academic Advice:</b>", styles["Heading3"]))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(advice, styles["Normal"]))
    elements.append(Spacer(1, 0.5 * inch))

    # =====================================
    # SIGNATURE
    # =====================================
    elements.append(Paragraph("______________________________", styles["Normal"]))
    elements.append(Paragraph("Controller of Examinations", styles["Normal"]))

    doc.build(elements, onFirstPage=add_watermark)

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')