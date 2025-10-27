"""
Unit tests for Patient Management API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date

from .models import Patient, Diagnosis

User = get_user_model()


class PatientModelTestCase(TestCase):
    """Test cases for Patient model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testdoc',
            email='doc@test.com',
            password='testpass123'
        )
    
    def test_create_patient(self):
        """Test creating a patient."""
        patient = Patient.objects.create(
            mrn='MRN001',
            full_name='John Doe',
            date_of_birth=date(1990, 1, 1),
            gender='male',
            phone='0812345678',
            email='john@example.com',
            address='123 Test St',
            created_by=self.user
        )
        
        self.assertEqual(patient.mrn, 'MRN001')
        self.assertEqual(patient.full_name, 'John Doe')
        self.assertEqual(patient.gender, 'male')
        self.assertIsNotNone(patient.created_at)
    
    def test_patient_age_calculation(self):
        """Test patient age calculation."""
        patient = Patient.objects.create(
            mrn='MRN002',
            full_name='Jane Doe',
            date_of_birth=date(2000, 1, 1),
            gender='female',
            created_by=self.user
        )
        
        # Age should be calculated correctly
        self.assertIsInstance(patient.age, int)
        self.assertGreaterEqual(patient.age, 0)


class PatientAPITestCase(TestCase):
    """Test cases for Patient API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testdoc',
            email='doc@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test patients
        self.patient1 = Patient.objects.create(
            mrn='MRN001',
            full_name='John Doe',
            date_of_birth=date(1990, 1, 1),
            gender='male',
            phone='0812345678',
            created_by=self.user
        )
        self.patient2 = Patient.objects.create(
            mrn='MRN002',
            full_name='Jane Smith',
            date_of_birth=date(1985, 5, 15),
            gender='female',
            phone='0823456789',
            created_by=self.user
        )
    
    def test_list_patients(self):
        """Test listing all patients."""
        response = self.client.get('/api/v1/patients/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.json())
        self.assertGreaterEqual(len(response.json()['results']), 2)
    
    def test_get_patient_detail(self):
        """Test getting patient detail."""
        response = self.client.get(f'/api/v1/patients/{self.patient1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['mrn'], 'MRN001')
        self.assertEqual(data['full_name'], 'John Doe')
    
    def test_create_patient(self):
        """Test creating a new patient."""
        data = {
            'mrn': 'MRN003',
            'full_name': 'Bob Johnson',
            'date_of_birth': '1995-03-20',
            'gender': 'male',
            'phone': '0834567890',
            'email': 'bob@example.com'
        }
        
        response = self.client.post('/api/v1/patients/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['mrn'], 'MRN003')
        self.assertEqual(Patient.objects.count(), 3)
    
    def test_update_patient(self):
        """Test updating patient information."""
        data = {
            'full_name': 'John Updated Doe',
            'phone': '0899999999'
        }
        
        response = self.client.patch(f'/api/v1/patients/{self.patient1.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.patient1.refresh_from_db()
        self.assertEqual(self.patient1.full_name, 'John Updated Doe')
        self.assertEqual(self.patient1.phone, '0899999999')
    
    def test_delete_patient(self):
        """Test deleting a patient."""
        patient_id = self.patient1.id
        response = self.client.delete(f'/api/v1/patients/{patient_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(id=patient_id).exists())
    
    def test_search_patients(self):
        """Test searching patients by name or MRN."""
        response = self.client.get('/api/v1/patients/?search=John')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()['results']
        self.assertGreaterEqual(len(results), 1)
        self.assertIn('John', results[0]['full_name'])
    
    def test_unauthorized_access(self):
        """Test that unauthenticated users cannot access patients."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/patients/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DiagnosisAPITestCase(TestCase):
    """Test cases for Diagnosis API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testdoc',
            email='doc@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.patient = Patient.objects.create(
            mrn='MRN001',
            full_name='John Doe',
            date_of_birth=date(1990, 1, 1),
            gender='male',
            created_by=self.user
        )
    
    def test_create_diagnosis(self):
        """Test creating a diagnosis for a patient."""
        data = {
            'patient': self.patient.id,
            'diagnosis': 'Labrador Retriever',
            'confidence': 0.95,
            'image_url': 'https://example.com/dog.jpg',
            'notes': 'Test diagnosis'
        }
        
        response = self.client.post('/api/v1/diagnoses/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['diagnosis'], 'Labrador Retriever')
        self.assertEqual(Diagnosis.objects.count(), 1)
    
    def test_list_patient_diagnoses(self):
        """Test listing diagnoses for a specific patient."""
        # Create diagnoses
        Diagnosis.objects.create(
            patient=self.patient,
            diagnosis='Breed A',
            confidence=0.90,
            created_by=self.user
        )
        Diagnosis.objects.create(
            patient=self.patient,
            diagnosis='Breed B',
            confidence=0.85,
            created_by=self.user
        )
        
        response = self.client.get(f'/api/v1/patients/{self.patient.id}/diagnoses/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 2)
