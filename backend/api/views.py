from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment, Patient, Doctor, AccessControl, MedicalRecord
from .serializers import AppointmentSerializer, PatientSerializer, DoctorSerializer, MessageSerializer, MedicalRecordSerializer
# from contracts.utils import create_appointment_onchain  # <-- add this later
import uuid  # for mock CID

@api_view(['GET'])
def get_appointments(request):
    appointments = Appointment.objects.all()
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def book_appointment(request):
    try:
        # validate that patient & doctor exist
        patient = Patient.objects.get(id=request.data['patient_id'])
        doctor = Doctor.objects.get(id=request.data['doctor_id'])

        data = {
            "patient": patient.id,
            "doctor": doctor.id,
            "symptoms": request.data["symptoms"],
            "datetime": request.data["datetime"],
            "status": "pending"
        }

        serializer = AppointmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Booked", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"}, status=404)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)
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

@api_view(['POST'])
def register_patient(request):
    serializer = PatientSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Patient registered", "data": serializer.data}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def get_patient(request, id):
    try:
        patient = Patient.objects.get(id=id)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"}, status=404)

@api_view(['GET'])
def list_patients(request):
    patients = Patient.objects.all()
    serializer = PatientSerializer(patients, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def register_doctor(request):
    serializer = DoctorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Doctor registered", "data": serializer.data}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def get_doctor(request, id):
    try:
        doctor = Doctor.objects.get(id=id)
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)

@api_view(['GET'])
def list_doctors(request):
    doctors = Doctor.objects.all()
    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def send_message(request):
    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Message sent", "data": serializer.data}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def grant_access(request):
    try:
        patient_id = request.data['patient_id']
        doctor_id = request.data['doctor_id']

        access, created = AccessControl.objects.get_or_create(
            patient_id=patient_id,
            doctor_id=doctor_id
        )

        if created:
            return Response({"message": "Access granted successfully."}, status=201)
        else:
            return Response({"message": "Access already exists."}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['POST'])
def upload_medical_record(request):
    try:
        patient_id = request.data.get('patient_id')
        file = request.FILES.get('file')
        description = request.data.get('description', '')

        if not file:
            return Response({"error": "No file uploaded."}, status=400)

        # 📦 TODO: Replace this with actual IPFS upload
        # For now, generate a mock CID
        fake_cid = f"Qm{uuid.uuid4().hex[:44]}"

        record = MedicalRecord.objects.create(
            patient_id=patient_id,
            ipfs_cid=fake_cid,
            description=description
        )

        serializer = MedicalRecordSerializer(record)
        return Response({"message": "Uploaded", "data": serializer.data}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=400)





