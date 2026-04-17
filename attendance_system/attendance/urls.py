from django.urls import path
from . import views

urlpatterns = [
    path("rfid/", views.rfid_login),
    path("student/", views.student_login),
    path("dashboard/", views.dashboard),
    path('download-pdf/', views.download_attendance_pdf, name='download_pdf'),
]