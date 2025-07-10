from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import Appointment

class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Register Patient
        self.patient_data = {
            "user": {
                "username": "john",
                "email": "john@example.com",
                "password": "1234"
            },
            "wallet_address": "0xabc123",
            "age": 30,
            "gender": "male"
        }
        res = self.client.post("/api/patients/register/", self.patient_data, format='json')
        self.patient_id = res.data['data']['id']

        # Register Doctor
        self.doctor_data = {
            "user": {
                "username": "drsmith",
                "email": "dr@clinic.com",
                "password": "docpass"
            },
            "wallet_address": "0xdoctor456",
            "specialty": "Cardiology"
        }
        res = self.client.post("/api/doctors/register/", self.doctor_data, format='json')
        self.doctor_id = res.data['data']['id']

    def test_book_appointment(self):
        data = {
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "symptoms": "Headache",
            "datetime": "2025-07-10T18:00:00Z"
        }
        res = self.client.post("/api/appointments/book/", data, format='json')
        self.assertEqual(res.status_code, 201)
        self.appointment_id = res.data['data']['id']

    def test_approve_appointment(self):
        # Book appointment first
        appt = self.client.post("/api/appointments/book/", {
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "symptoms": "Back pain",
            "datetime": "2025-07-10T18:00:00Z"
        }, format='json')
        appt_id = appt.data['data']['id']

        res = self.client.post(f"/api/appointments/{appt_id}/approve/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['message'], "Appointment approved")

    def test_reject_appointment(self):
        # Book appointment first
        appt = self.client.post("/api/appointments/book/", {
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "symptoms": "Sore throat",
            "datetime": "2025-07-10T18:00:00Z"
        }, format='json')
        appt_id = appt.data['data']['id']

        res = self.client.post(f"/api/appointments/{appt_id}/reject/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['message'], "Appointment rejected")
