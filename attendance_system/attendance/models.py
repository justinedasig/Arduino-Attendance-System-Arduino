from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)   # keypad input
    rfid_uid = models.CharField(max_length=50, unique=True)      # RFID card
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.student_id})"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    time_in = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.time_in}"