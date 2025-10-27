"""Unit tests for Patient Management API."""
import unittest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from .models import Patient

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
            age=34,
            gender='M',
            phone='0812345678',
            notes='Test patient',
            created_by=self.user
        )
        
        self.assertEqual(patient.mrn, 'MRN001')
        self.assertEqual(patient.full_name, 'John Doe')
        self.assertEqual(patient.gender, 'M')
        self.assertEqual(patient.age, 34)
        self.assertIsNotNone(patient.created_at)
    
    def test_patient_age_field(self):
        """Test patient age field."""
        patient = Patient.objects.create(
            mrn='MRN002',
            full_name='Jane Doe',
            age=24,
            gender='F',
            created_by=self.user
        )
        
        # Age should be stored correctly
        self.assertIsInstance(patient.age, int)
        self.assertEqual(patient.age, 24)


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
            age=34,
            gender='M',
            phone='0812345678',
            created_by=self.user
        )
        self.patient2 = Patient.objects.create(
            mrn='MRN002',
            full_name='Jane Smith',
            age=39,
            gender='F',
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
            'age': 29,
            'gender': 'M',
            'phone': '0834567890'
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
    
    @unittest.skip("DELETE endpoint not implemented yet")
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


# Note: Diagnosis functionality is handled through Transaction model
# These tests are covered in predictions.tests
