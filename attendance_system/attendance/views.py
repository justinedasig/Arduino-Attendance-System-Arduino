from django.http import JsonResponse
from django.shortcuts import render
from .models import Student, Attendance


# RFID LOGIN
def rfid_login(request):
    uid = request.GET.get("uid")

    try:
        student = Student.objects.get(rfid_uid=uid)
        Attendance.objects.create(student=student)

        return JsonResponse({
            "status": "success",
            "message": f"{student.name} logged in via RFID"
        })

    except Student.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "RFID not registered"
        })


# KEYBOARD LOGIN
def student_login(request):
    sid = request.GET.get("id")

    try:
        student = Student.objects.get(student_id=sid)
        Attendance.objects.create(student=student)

        return JsonResponse({
            "status": "success",
            "message": f"{student.name} logged in via ID"
        })

    except Student.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Student ID not found"
        })
# DASHBOARD VIEW
def dashboard(request):
    logs = Attendance.objects.all().order_by('-time_in')
    return render(request, "attendance/dashboard.html", {"logs": logs})