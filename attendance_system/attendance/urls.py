from django.urls import path
from . import views

urlpatterns = [
    path("rfid/", views.rfid_login),
    path("student/", views.student_login),
    path("dashboard/", views.dashboard),  # ADD THIS
]