from apscheduler.schedulers.background import BackgroundScheduler
from django.core.mail import send_mail
from datetime import datetime, timedelta
from .models import Timetable


def send_reminders():
    now = datetime.now()
    upcoming_time = (now + timedelta(minutes=10)).time()
    today = now.strftime('%A')

    lectures = Timetable.objects.filter(
        day=today,
        start_time=upcoming_time
    )

    for lecture in lectures:
        send_mail(
            'Lecture Reminder',
            f'Your lecture "{lecture.subject}" starts in 10 minutes.',
            'your_email@gmail.com',
            [lecture.teacher.email],
            fail_silently=False,
        )


def start_scheduler():   # 👈 THIS NAME MUST MATCH
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_reminders, 'interval', minutes=1)
    scheduler.start()
