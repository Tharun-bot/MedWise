from django.urls import path
from . import views

urlpatterns = [
    # Existing appointment routes
    path('appointments/', views.get_appointments),
    path('appointments/book/', views.book_appointment),
    path('appointments/<int:id>/approve/', views.approve_appointment),
    path('appointments/<int:id>/reject/', views.reject_appointment),

    # ✅ Add these doctor routes
    path('doctors/register/', views.register_doctor),
    path('doctors/<int:id>/', views.get_doctor),
    path('doctors/', views.list_doctors),

    # (Optional) patient routes if not yet added
    path('patients/register/', views.register_patient),
    path('patients/<int:id>/', views.get_patient),
    path('patients/', views.list_patients),
]
