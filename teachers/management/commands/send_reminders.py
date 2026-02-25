from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from attendance.models import Timetable
from datetime import timedelta


class Command(BaseCommand):
    help = "Send email reminder 10 minutes before lecture"

    def handle(self, *args, **kwargs):

        now = timezone.localtime()
        target_time = now + timedelta(minutes=10)
        current_day = now.strftime("%a")

        todays_classes = Timetable.objects.filter(
            day=current_day
        ).select_related("teacher", "subject")

        found = False

        for entry in todays_classes:

            lecture_datetime = timezone.make_aware(
                timezone.datetime.combine(now.date(), entry.start_time)
            )

            difference = (lecture_datetime - now).total_seconds() / 60

            if 8 <= difference <= 12:

                teacher = entry.teacher

                if teacher.user.email:
                    send_mail(
                        subject="Lecture Reminder",
                        message=f"""
Hello {teacher.user.first_name},

Reminder: Your lecture for {entry.subject.name}
starts at {entry.start_time}.

Please be ready.

Smart Attendance System
                        """,
                        from_email=None,
                        recipient_list=[teacher.user.email],
                        fail_silently=False,
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Reminder sent to {teacher.user.email}"
                        )
                    )

                    found = True

        if not found:
            self.stdout.write("No lectures to remind.")