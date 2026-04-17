from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from .models import Student, Attendance
import io
from xhtml2pdf import pisa
from django.template.loader import get_template

def handle_attendance_logic(student):
    """Helper function to calculate IN/OUT toggle and duration."""
    now = timezone.now()
    last_log = Attendance.objects.filter(student=student).order_by('-timestamp').first()

    if not last_log or last_log.status == 'OUT':
        new_status = 'IN'
        duration = None
    else:
        new_status = 'OUT'
        duration = now - last_log.timestamp

    Attendance.objects.create(
        student=student,
        status=new_status,
        timestamp=now,
        duration=duration
    )
    return new_status

# RFID LOGIN
def rfid_login(request):
    uid = request.GET.get("uid")
    try:
        student = Student.objects.get(rfid_uid=uid)
        status = handle_attendance_logic(student)
        return JsonResponse({"status": "success", "message": f"{student.name} marked as {status}"})
    except Student.DoesNotExist:
        return JsonResponse({"status": "error", "message": "RFID not registered"})

# KEYBOARD LOGIN
def student_login(request):
    sid = request.GET.get("id")
    try:
        student = Student.objects.get(student_id=sid)
        status = handle_attendance_logic(student)
        return JsonResponse({"status": "success", "message": f"{student.name} marked as {status}"})
    except Student.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Student ID not found"})

# DASHBOARD VIEW
def dashboard(request):
    today = timezone.now().date()
    all_students = Student.objects.all()
    
    # 1. Get logs for the table (limited to today)
    logs = Attendance.objects.filter(timestamp__date=today).order_by('-timestamp')

    # 2. Logic for Present, Cutting, and Absent
    present_students = []
    cutting_students = []
    
    # Get IDs of students who checked in at least once today
    checked_in_ids = Attendance.objects.filter(
        timestamp__date=today
    ).values_list('student_id', flat=True).distinct()
    
    absent_students = all_students.exclude(id__in=checked_in_ids)
    
    # Determine if checked-in students are currently IN or OUT
    students_who_showed_up = all_students.filter(id__in=checked_in_ids)
    for student in students_who_showed_up:
        latest_log = Attendance.objects.filter(
            student=student, 
            timestamp__date=today
        ).latest('timestamp')
        
        if latest_log.status == 'IN':
            present_students.append(student)
        else:
            cutting_students.append(student)

    return render(request, "attendance/dashboard.html", {
        "logs": logs,
        "present_count": len(present_students),
        "cutting_count": len(cutting_students),
        "absent_count": absent_students.count(),
        "cutting_students": cutting_students,
        "absent_students": absent_students,
    })

# PDF REPORT
def download_attendance_pdf(request):
    today = timezone.now().date()
    all_students = Student.objects.all()
    
    # Logic to separate students into 3 lists
    present_students = []
    cutting_students = []
    
    checked_in_ids = Attendance.objects.filter(
        timestamp__date=today
    ).values_list('student_id', flat=True).distinct()
    
    absent_students = all_students.exclude(id__in=checked_in_ids)
    
    students_who_showed_up = all_students.filter(id__in=checked_in_ids)
    for student in students_who_showed_up:
        latest_log = Attendance.objects.filter(
            student=student, 
            timestamp__date=today
        ).latest('timestamp')
        
        if latest_log.status == 'IN':
            present_students.append(student)
        else:
            cutting_students.append(student)

    context = {
        'today': today,
        'present_students': present_students,
        'cutting_students': cutting_students,
        'absent_students': absent_students,
        'present_count': len(present_students),
        'cutting_count': len(cutting_students),
        'absent_count': absent_students.count(),
    }
    
    template = get_template('attendance/pdf_report.html')
    html = template.render(context)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Attendance_Summary_{today}.pdf"'
        return response
    
    return HttpResponse("Error generating PDF", status=400)