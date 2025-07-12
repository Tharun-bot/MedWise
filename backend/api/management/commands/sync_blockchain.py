from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Patient, Doctor
from contracts.web3_utils import contract, web3

class Command(BaseCommand):
    help = 'Sync doctors and patients from blockchain to database'

    def handle(self, *args, **kwargs):
        accounts = web3.eth.accounts
        for address in accounts:
            # Check if it's a patient
            try:
                patient_data = contract.functions.patients(address).call()
                if patient_data[4]:  # patient.exists == True
                    name, email, age, gender, _ = patient_data

                    if not Patient.objects.filter(wallet_address=address).exists():
                        username = email.split('@')[0]
                        user = User.objects.create_user(username=username, password='defaultpass')
                        Patient.objects.create(user=user, wallet_address=address, age=age, gender=gender)
                        self.stdout.write(self.style.SUCCESS(f"Synced patient: {email}"))

            except Exception:
                pass

            # Check if it's a doctor
            try:
                doctor_data = contract.functions.doctors(address).call()
                if doctor_data[3]:  # doctor.exists == True
                    name, email, specialty, _ = doctor_data

                    if not Doctor.objects.filter(wallet_address=address).exists():
                        username = email.split('@')[0]
                        user = User.objects.create_user(username=username, password='defaultpass')
                        Doctor.objects.create(user=user, wallet_address=address, specialty=specialty)
                        self.stdout.write(self.style.SUCCESS(f"Synced doctor: {email}"))

            except Exception:
                pass
