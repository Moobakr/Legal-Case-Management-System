from datetime import timezone
from django.db import models
from django.contrib.auth.models import User
import os


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ]

    CITY_CHOICES = [
        ('Cairo', 'Cairo'),
        ('Giza', 'Giza'),
        ('Alexandria', 'Alexandria'),
        ('Nasr City', 'Nasr City'),
        ('Mansoura', 'Mansoura'),
        ('Tanta', 'Tanta'),
        ('Asyut', 'Asyut'),
        ('Fayoum', 'Fayoum'),
        ('Zagazig', 'Zagazig'),
        ('Ismailia', 'Ismailia'),
        ('Luxor', 'Luxor'),
        ('Aswan', 'Aswan'),
    ]
    
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    first_name_ar = models.CharField(max_length=100)
    last_name_ar = models.CharField(max_length=100)
    first_name_en = models.CharField(max_length=100)
    last_name_en = models.CharField(max_length=100)
    national_id = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100, choices=CITY_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.first_name_en} {self.last_name_en})"


class Lawyer(models.Model):
    CASE_TYPES = (
        ('civil', 'Civil'),
        ('criminal', 'Criminal'),
        ('family', 'Family'),
        ('labor', 'Labor'),
        ('commercial', 'Commercial'),
    )

    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    full_name = models.CharField(max_length=200, default='')
    specialization = models.CharField(max_length=50, choices=CASE_TYPES, default='civil')
    license_number = models.CharField(max_length=50, unique=True)
    office_name = models.CharField(max_length=200, default='')
    office_address = models.TextField(default='')
    fax_no = models.CharField(max_length=50, default='')
    phone = models.CharField(max_length=20, default='')
    email = models.EmailField(unique=True, default='lawyer@example.com')
    available = models.BooleanField(default=True)
    location = models.CharField(max_length=100, choices=Client.CITY_CHOICES, default='Cairo')
    years_of_experience = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    bar_association_id = models.CharField(max_length=50, default='')
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Percentage of successful cases
    total_cases = models.IntegerField(default=0)  # Total number of cases handled
    bio = models.TextField(default='')  # Lawyer's biography and expertise
    languages = models.CharField(max_length=200, default='Arabic, English')  # Languages spoken
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Initial consultation fee
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.get_specialization_display()} ({self.location})"

    def get_success_rate_display(self):
        return f"{self.success_rate}%"

    def get_consultation_fee_display(self):
        return f"EGP {self.consultation_fee:,.2f}"


class Court(models.Model):
    JURISDICTION_LEVELS = (
        ('National', 'National'),
        ('Governorate', 'Governorate'),
        ('District', 'District'),
    )
    name = models.CharField(max_length=200, default='')
    location = models.CharField(max_length=200, default='')  # City name
    specialization = models.CharField(max_length=100, default='General')
    jurisdiction_level = models.CharField(
        max_length=20,
        choices=JURISDICTION_LEVELS,
        default='District'
    )

    def __str__(self):
        return self.name


def case_document_path(instance, filename):
    # Generate path: case_documents/case_id/filename
    return f'case_documents/{instance.case.id}/{filename}'

class CaseDocument(models.Model):
    DOCUMENT_TYPES = (
        ('evidence', 'Evidence'),
        ('contract', 'Contract'),
        ('report', 'Report'),
        ('photo', 'Photo'),
        ('other', 'Other'),
    )
    
    case = models.ForeignKey('LawsuitCase', on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=case_document_path)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_document_type_display()}"

class CaseParticipant(models.Model):
    ROLE_CHOICES = (
        ('plaintiff', 'Plaintiff'),
        ('defendant', 'Defendant'),
        ('witness', 'Witness'),
        ('expert', 'Expert Witness'),
        ('other', 'Other'),
    )
    
    case = models.ForeignKey('LawsuitCase', on_delete=models.CASCADE, related_name='participants')
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    contact_info = models.TextField()
    address = models.TextField()
    national_id = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_role_display()}"

class LawsuitCase(models.Model):
    CASE_TYPES = (
        ('civil', 'Civil'),
        ('criminal', 'Criminal'),
        ('family', 'Family'),
        ('labor', 'Labor'),
        ('commercial', 'Commercial'),
    )

    title = models.CharField(max_length=255, default='Untitled Case')
    case_type = models.CharField(max_length=50, choices=CASE_TYPES, default='civil')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    lawyer = models.ForeignKey(Lawyer, on_delete=models.SET_NULL, null=True, blank=True)
    court = models.ForeignKey(Court, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(default='No description provided.')
    date_filed = models.DateField(default=timezone)
    status = models.CharField(max_length=50, default='Open')
    verdict = models.TextField(null=True, blank=True)
    verdict_date = models.DateField(null=True, blank=True)
    next_hearing_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_case_type_display()} case: {self.title} by {self.client.username if self.client else 'Unknown'}"
    
    def get_documents(self):
        return self.documents.all().order_by('-uploaded_at')
    
    def get_participants(self):
        return self.participants.all().order_by('role', 'name')