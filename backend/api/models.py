from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_address = models.CharField(max_length=200, unique=True)   #For the safe wallet address for each user
    age = models.IntegerField()
    gender = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_address = models.CharField(max_length=200, unique=True)
    specialty = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
    
class Appointment(models.Model):
    STATUS_CHOICE = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    symptoms = models.DateTimeField()
    datetime = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE)

    def __str__(self):
        return f"{self.patient.user.username} --> {self.doctor.user.username} at {self.datetime}"
    
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recieved')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username} --> {self.receiver.username}'


class AccessControl(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient', 'doctor')
    
    def __str__(self):
        return f"{self.patient.user.username} --> {self.doctor.user.username}"
    
class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    ipfs_cid = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"CID: {self.ipfs_cid} for {self.patient.user.username}"

class HealthReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    fasting_glucose = models.FloatField()
    hba1c = models.FloatField()
    uric_acid = models.FloatField()
    creatinine = models.FloatField()
    hemoglobin = models.FloatField()
    total_cholesterol = models.FloatField()
    ldl = models.FloatField()
    hdl = models.FloatField()
    vitamin_d = models.FloatField()
    hs_crp = models.FloatField()

    notes = models.TextField(blank=True, null=True)
