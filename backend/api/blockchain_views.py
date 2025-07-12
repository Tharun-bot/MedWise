"""from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment, Patient, Doctor, AccessControl, MedicalRecord
from .serializers import AppointmentSerializer, PatientSerializer, DoctorSerializer, MessageSerializer, MedicalRecordSerializer
# from contracts.utils import create_appointment_onchain  # <-- add this later
import uuid  # for mock CID
from contracts.web3_utils import w3, contract, WALLET_ADDRESS, PRIVATE_KEY
import time

@api_view(['GET'])
def get_appointments(request):
    try:
        appointments = Appointment.objects.all().order_by('-datetime')
        serializer = AppointmentSerializer(appointments, many=True)

        return Response({
            "count": appointments.count(),
            "data": serializer.data
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def book_appointment(request):
    try:
        patient = Patient.objects.get(id=request.data['patient_id'])
        doctor = Doctor.objects.get(id=request.data['doctor_id'])

        symptoms = request.data["symptoms"]
        datetime = request.data["datetime"]

        # Convert datetime to UNIX timestamp (or use int(timestamp) if already numeric)
        timestamp = int(time.mktime(time.strptime(datetime, "%Y-%m-%d %H:%M:%S")))

        # On-chain call: bookAppointment(doctor_address, symptoms, timestamp)
        nonce = w3.eth.get_transaction_count(patient.wallet_address)

        txn = contract.functions.bookAppointment(
            doctor.wallet_address,
            symptoms,
            timestamp
        ).build_transaction({
            'from': patient.wallet_address,
            'nonce': nonce,
            'gas': 3000000,
            'gasPrice': w3.to_wei('20', 'gwei')
        })

        signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return Response({
            "message": "Appointment booked on-chain",
            "transaction_hash": w3.to_hex(tx_hash)
        }, status=201)

    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"}, status=404)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


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
        try:
            # Save to DB
            patient = serializer.save()

            # Extract on-chain fields
            name = serializer.validated_data['user']['username']
            email = serializer.validated_data['user']['email']
            age = serializer.validated_data['age']
            gender = serializer.validated_data['gender']
            wallet = serializer.validated_data['wallet_address']

            # Prepare transaction
            nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
            txn = contract.functions.registerPatient(name, email, age, gender).build_transaction({
                'from': WALLET_ADDRESS,
                'nonce': nonce,
                'gas': 3000000,
                'gasPrice': w3.to_wei('20', 'gwei')
            })

            signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            w3.eth.wait_for_transaction_receipt(tx_hash)

            return Response({"message": "Patient registered", "data": serializer.data}, status=201)

        except ValueError as e:
            err = str(e)
            if "Already registered as patient" in err:
                return Response({"error": "Already registered on chain"}, status=400)
            return Response({"error": err}, status=500)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def get_patient_onchain(request, address):
    try:
        patient = contract.functions.patients(address).call()
        if not patient[4]:  # `exists` is the 5th element
            return Response({"error": "Patient not found"}, status=404)

        data = {
            "name": patient[0],
            "email": patient[1],
            "age": patient[2],
            "gender": patient[3],
        }
        return Response(data)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


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
        try:
            doctor = serializer.save()

            name = serializer.validated_data['user']['username']
            email = serializer.validated_data['user']['email']
            specialty = serializer.validated_data['specialty']

            nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)

            txn = contract.functions.registerDoctor(
                name, email, specialty
            ).build_transaction({
                'from': WALLET_ADDRESS,
                'nonce': nonce,
                'gas': 3000000,
                'gasPrice': w3.to_wei('20', 'gwei'),
                'chainId': 31337  # ✅ Hardhat
            })

            signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            w3.eth.wait_for_transaction_receipt(tx_hash)

            return Response({"message": "Doctor registered", "tx_hash": tx_hash.hex(), "data": serializer.data}, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

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


@api_view(['GET'])
def doctor_patients(request, id):
    try:
        patients = AccessControl.objects.filter(doctor_id=id).select_related('patient')
        data = [PatientSerializer(ac.patient).data for ac in patients]
        return Response(data)
    except:
        return Response({"error": "No patients or access issue"}, status=404)

@api_view(['GET'])
def patient_records(request, id):
    try:
        records = MedicalRecord.objects.filter(patient_id=id)
        from .serializers import MedicalRecordSerializer
        serializer = MedicalRecordSerializer(records, many=True)
        return Response(serializer.data)
    except:
        return Response({"error": "No records found"}, status=404)
    

@api_view(['POST'])
def symptom_triage(request):
    symptoms = request.data.get("symptoms")
    if not symptoms:
        return Response({"error": "Symptoms required"}, status=400)

    # Mock AI model output (replace with actual LLM call later)
    mock_output = {
        "severity": "mild",  # e.g. safe, mild, uncertain, emergency
        "recommended_action": "Take rest and stay hydrated. Visit a doctor if it worsens."
    }

    return Response({"result": mock_output})

@api_view(['POST'])
def mental_health_bot(request):
    query = request.data.get("query")
    if not query:
        return Response({"error": "Query required"}, status=400)

    # Mock response from LLM (replace with real model inference)
    reply = "I'm sorry you're feeling this way. Remember, you're not alone. Would you like to talk more?"

    return Response({"response": reply})

@api_view(['POST'])
def meal_plan(request):
    health_params = request.data.get("health_params", "normal")

    # Placeholder response — replace with real API call (e.g., Edamam)
    recommendations = {
        "diabetes": ["Low-carb salad", "Grilled chicken", "Steamed broccoli"],
        "hypertension": ["Oats", "Low-sodium soup", "Fruits"],
        "normal": ["Balanced meal", "Rice + dal", "Vegetable stir fry"]
    }

    meals = recommendations.get(health_params.lower(), recommendations["normal"])
    return Response({"meals": meals})"""


# backend/api/blockchain_views.py

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from web3.exceptions import ContractLogicError
from contracts.web3_utils import web3, contract, WALLET_ADDRESS, PRIVATE_KEY

@api_view(['POST'])
def register_doctor(request):
    try:
        data = request.data
        name = data['name']
        email = data['email']
        speciality = data['speciality']

        nonce = web3.eth.get_transaction_count(WALLET_ADDRESS)

        tx = contract.functions.registerDoctor(name, email, speciality).build_transaction({
            "from": WALLET_ADDRESS,
            "nonce": nonce,
            "gas": 3000000,
            "gasPrice": web3.to_wei("20", "gwei")
        })

        signed_tx = web3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)


        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        return JsonResponse({'status': 'Doctor registered', 'tx_hash': tx_hash.hex()})

    except ContractLogicError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected: {str(e)}'}, status=500)


@api_view(['POST'])
def register_patient(request):
    try:
        data = request.data
        name = data['name']
        email = data['email']
        age = int(data['age'])
        gender = data['gender']

        nonce = web3.eth.get_transaction_count(WALLET_ADDRESS)

        tx = contract.functions.registerPatient(name, email, age, gender).build_transaction({
            "from": WALLET_ADDRESS,
            "nonce": nonce,
            "gas": 3000000,
            "gasPrice": web3.to_wei("20", "gwei")
        })

        signed_tx = web3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)  # ✅ fixed here

        return JsonResponse({'status': 'Patient registered', 'tx_hash': tx_hash.hex()})

    except ContractLogicError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected: {str(e)}'}, status=500)





