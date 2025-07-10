from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_address = models.CharField(max_length=100, unique=True)   #For the safe wallet address for each user
    age = models.IntegerField()
    gender = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_address = models.CharField(max_length=100, unique=True)
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
    symptons = models.TextField()
    datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICE)

    def __str__(self):
        return f"{self.patient.user.username} --> {self.doctor.user.username} at {self.datetime}"
    
    