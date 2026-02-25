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
@login_required
def student_results(request):
    if not hasattr(request.user, 'student'):
        return redirect('teacher_dashboard')

    student = request.user.student
    semester = student.semester

    # ✅ Correct filtering
    internal_records = InternalMarks.objects.filter(
        student=student,
        subject__semester=semester
    )

    if not internal_records.exists():
        return render(request, "students/results.html", {
            "error": "No subjects found for this semester."
        })

    subject_results = []
    total_marks = 0

    for record in internal_records:
        subject_name = record.subject.name
        marks = record.marks
        total_marks += marks

        subject_results.append({
            "subject": subject_name,
            "marks": marks
        })

    total_subjects = internal_records.count()

    # ✅ Each subject is out of 15 (not 100)
    percentage = (total_marks / (total_subjects * 15)) * 100

    # Grade logic
    if percentage >= 90:
        grade = "A"
        status = "PASS"
    elif percentage >= 75:
        grade = "B"
        status = "PASS"
    elif percentage >= 50:
        grade = "C"
        status = "PASS"
    else:
        grade = "F"
        status = "FAIL"

    context = {
        "subject_results": subject_results,
        "total": total_marks,
        "percentage": round(percentage, 2),
        "grade": grade,
        "status": status,
        "semester": semester
    }

    return render(request, "students/results.html", context)
    # =====================================================
# MANUAL RESULT GENERATOR (Student Self Calculation)
# =====================================================
@login_required
def manual_result(request):
    if not hasattr(request.user, 'student'):
        return redirect('teacher_dashboard')

    results = []
    total = 0

    if request.method == "POST":
        subjects = request.POST.getlist('subject')
        marks = request.POST.getlist('marks')

        for subject, mark in zip(subjects, marks):
            try:
                mark = int(mark)
            except:
                mark = 0

            total += mark

            results.append({
                "subject": subject,
                "marks": mark
            })

        return render(request, "students/manual_result.html", {
            "results": results,
            "total": total
        })

    return render(request, "students/manual_result.html")


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

        request.session['pdf_data'] = {
            'results': results,
            'total': total,
            'percentage': percentage,
            'grade': grade,
            'status': status
        }

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

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from django.http import HttpResponse
import io


from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.utils.timezone import now
import io
import os


@login_required
def download_pdf(request):
    data = request.session.get('pdf_data')

    if not data:
        return redirect('predict_result')

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # =========================
    # COLLEGE LOGO
    # =========================
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'kaveri_logo.png')

    if os.path.exists(logo_path):
        logo = Image(logo_path, 1.2 * inch, 1.2 * inch)
        elements.append(logo)

    elements.append(Spacer(1, 0.2 * inch))

    # =========================
    # TITLE
    # =========================
    elements.append(Paragraph("<b>OFFICIAL STUDENT RESULT REPORT</b>", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))

    # =========================
    # STUDENT INFO
    # =========================
    student_name = request.user.username
    elements.append(Paragraph(f"<b>Student Name:</b> {student_name}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Date Generated:</b> {now().strftime('%d %B %Y')}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # =========================
    # TABLE
    # =========================
    table_data = [["Subject", "Marks"]]

    for r in data['results']:
        table_data.append([r['subject'], r['marks']])

    table = Table(table_data, colWidths=[3 * inch, 2 * inch])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))

    # =========================
    # SUMMARY
    # =========================
    elements.append(Paragraph(f"<b>Total:</b> {data['total']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Percentage:</b> {data['percentage']}%", styles["Normal"]))
    elements.append(Paragraph(f"<b>Grade:</b> {data['grade']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Status:</b> {data['status']}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # =========================
    # PERFORMANCE BADGE
    # =========================
    percentage = data['percentage']

    if percentage >= 90:
        badge = "🏆 Outstanding Performer"
        advice = "Excellent academic performance. Keep up the exceptional work!"
    elif percentage >= 75:
        badge = "🎖 Very Good Performance"
        advice = "Strong performance. Aim for higher consistency."
    elif percentage >= 50:
        badge = "👍 Satisfactory Performance"
        advice = "You passed. Focus on improving weaker subjects."
    else:
        badge = "⚠ Needs Improvement"
        advice = "Significant improvement required. Seek academic guidance."

    elements.append(Paragraph(f"<b>Performance Badge:</b> {badge}", styles["Heading3"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("<b>Personalized Advice:</b>", styles["Heading3"]))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(advice, styles["Normal"]))
    elements.append(Spacer(1, 0.5 * inch))

    # =========================
    # SIGNATURE LINE
    # =========================
    elements.append(Paragraph("__________________________", styles["Normal"]))
    elements.append(Paragraph("Authorized Signature", styles["Normal"]))

    # =========================
    # WATERMARK
    # =========================
    def add_watermark(canvas_obj, doc):
        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica", 60)
        canvas_obj.setFillColorRGB(0.9, 0.9, 0.9)
        canvas_obj.drawCentredString(300, 400, "CONFIDENTIAL")
        canvas_obj.restoreState()

    doc.build(elements, onFirstPage=add_watermark)

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')