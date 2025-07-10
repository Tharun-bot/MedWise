from django.urls import path
from . import views

urlpatterns = [
    path('appointments/', views.get_appointments),
    path('appointments/book/', views.book_appointment),
    path('appointments/<int:id>/approve/', views.approve_appointment),
    path('appointments/<int:id>/reject/', views.reject_appointment),
]
