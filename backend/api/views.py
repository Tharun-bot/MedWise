from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Appointment
from .serializers import AppointmentSerializer
from django.http import JsonResponse
# Create your views here.

def home(request):
    return JsonResponse({"message" : "MedWise API"})

@api_view(['GET'])
def get_appointments(request):
    appointments = Appointment.objects.all()
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)