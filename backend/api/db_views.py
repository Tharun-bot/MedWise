# backend/api/db_views.py
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Patient, Doctor

from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def register_patient(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')
        wallet_address = data.get('wallet_address')
        age = data.get('age')
        gender = data.get('gender')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, password=password)
        patient = Patient.objects.create(user=user, wallet_address=wallet_address, age=age, gender=gender)

        return JsonResponse({'message': 'Patient registered successfully'})
    return JsonResponse({'error': 'Only POST allowed'}, status=405)


@csrf_exempt
def register_doctor(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')
        wallet_address = data.get('wallet_address')
        specialty = data.get('specialty')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, password=password)
        doctor = Doctor.objects.create(user=user, wallet_address=wallet_address, specialty=specialty)

        return JsonResponse({'message': 'Doctor registered successfully'})
    return JsonResponse({'error': 'Only POST allowed'}, status=405)
