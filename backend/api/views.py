from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment, Patient, Doctor
from .serializers import AppointmentSerializer
# from contracts.utils import create_appointment_onchain  # <-- add this later

@api_view(['GET'])
def get_appointments(request):
    appointments = Appointment.objects.all()
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def book_appointment(request):
    try:
        patient = Patient.objects.get(id=request.data['patient_id'])
        doctor = Doctor.objects.get(id=request.data['doctor_id'])
        symptoms = request.data['symptoms']
        datetime = request.data['datetime']

        # tx_hash = create_appointment_onchain(...)  # placeholder

        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            symptoms=symptoms,
            datetime=datetime,
            status='pending'
        )
        serializer = AppointmentSerializer(appointment)
        return Response({"message": "Booked", "data": serializer.data}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def approve_appointment(request, id):
    try:
        appt = Appointment.objects.get(id=id)
        appt.status = 'approved'
        appt.save()
        return Response({"message": "Appointment approved"})
    except Appointment.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

@api_view(['POST'])
def reject_appointment(request, id):
    try:
        appt = Appointment.objects.get(id=id)
        appt.status = 'rejected'
        appt.save()
        return Response({"message": "Appointment rejected"})
    except Appointment.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
