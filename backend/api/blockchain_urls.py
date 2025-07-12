# backend/api/blockchain_urls.py
# backend/api/blockchain_urls.py

from django.urls import path
from . import blockchain_views as views

urlpatterns = [
    path('register-doctor/', views.register_doctor, name='register_doctor'),
    path('register-patient/', views.register_patient, name='register_patient'),
]

