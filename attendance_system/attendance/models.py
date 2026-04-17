from django.db import models
from django.utils import timezone

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    rfid_uid = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.student_id})"

    @property
    def current_attendance_status(self):
        """
        Returns 'Present' if the student has at least one log today, 
        otherwise returns 'Absent'.
        """
        today = timezone.now().date()
        # Check if any Attendance record exists for this student today
        has_log_today = Attendance.objects.filter(
            student=self, 
            timestamp__date=today
        ).exists()
        
        return "Present" if has_log_today else "Absent"
    @property
    def is_cutting(self):
        """Returns True if the last log today was 'OUT'."""
        today = timezone.now().date()
        last_log = Attendance.objects.filter(
            student=self, 
            timestamp__date=today
        ).order_by('-timestamp').first()
        
        return last_log is not None and last_log.status == 'OUT'

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('IN', 'Entered'),
        ('OUT', 'Exited'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    duration = models.DurationField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
