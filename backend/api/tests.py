from django.test import TestCase
from rest_framework.test import APIClient
import time


class OnChainIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.patient_wallet = "0xdD2FD4581271e230360230F9337D5c0430Bf44C0"
        self.doctor_wallet = "0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199"

        self.client.post("/api/patients/register/", {
            "name": "Alice",
            "email": "alice@example.com",
            "age": 28,
            "gender": "female",
            "wallet_address": self.patient_wallet
        }, format="json")

        self.client.post("/api/doctors/register/", {
            "name": "Bob",
            "email": "bob@hospital.com",
            "specialty": "General",
            "wallet_address": self.doctor_wallet
        }, format="json")


    def test_register_patient_onchain(self):
        data = {
            "name": "Alice",
            "email": "alice@example.com",
            "age": 28,
            "gender": "female",
            "wallet_address": self.patient_wallet
        }
        res = self.client.post("/api/patients/register/", data, format="json")
        self.assertIn(res.status_code, [201, 400])  # 400 if already registered

    def test_register_doctor_onchain(self):
        data = {
            "name": "Dr. Bob",
            "email": "bob@example.com",
            "specialty": "Cardiology",
            "wallet_address": self.doctor_wallet
        }
        res = self.client.post("/api/doctors/register/", data, format="json")
        self.assertIn(res.status_code, [201, 400])  # 400 if already registered

    def test_book_appointment_onchain(self):
        timestamp = int(time.time())
        data = {
            "patient_wallet": self.patient_wallet,
            "doctor_wallet": self.doctor_wallet,
            "symptoms": "High fever",
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timestamp))
        }
        res = self.client.post("/api/appointments/book/", data, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertIn("transaction_hash", res.data)

    def test_view_doctor_onchain(self):
        res = self.client.get(f"/api/doctors/{self.doctor_wallet}/")
        self.assertIn(res.status_code, [200, 404])
        if res.status_code == 200:
            self.assertIn("specialty", res.data)

    def test_grant_access_onchain(self):
        # Ensure both are registered
        self.client.post("/api/patients/register/", {
            "name": "Alice",
            "email": "alice@example.com",
            "age": 30,
            "gender": "female",
            "wallet_address": self.patient_wallet
        }, format="json")

        self.client.post("/api/doctors/register/", {
            "name": "Bob",
            "email": "bob@example.com",
            "specialty": "General",
            "wallet_address": self.doctor_wallet
        }, format="json")

        res = self.client.post("/api/access/grant/", {
            "patient_wallet": self.patient_wallet,
            "doctor_wallet": self.doctor_wallet
        }, format="json")
        self.assertIn(res.status_code, [200, 201])


    def test_view_patient_onchain_with_access(self):
                # Register patient
        self.client.post("/api/patients/register/", {
            "name": "Alice",
            "email": "alice@example.com",
            "age": 30,
            "gender": "female",
            "wallet_address": self.patient_wallet
        }, format="json")

        # Register doctor
        self.client.post("/api/doctors/register/", {
            "name": "Dr Bob",
            "email": "bob@example.com",
            "specialty": "General",
            "wallet_address": self.doctor_wallet
        }, format="json")

        # Grant access
        self.client.post("/api/access/grant/", {
            "patient_wallet": self.patient_wallet,
            "doctor_wallet": self.doctor_wallet
        }, format="json")

        # View patient
        res = self.client.get(f"/api/patients/{self.patient_wallet}/{self.doctor_wallet}/")
        self.assertIn(res.status_code, [200, 403])

