# backend/api/db_urls.py
from django.urls import path
from . import db_views as views  # ✅ correct import

urlpatterns = [
    path('register-patient/', views.register_patient),
    path('register-doctor/', views.register_doctor),
]
