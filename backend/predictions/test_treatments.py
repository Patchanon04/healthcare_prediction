"""
Unit tests for Treatment Management API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta

from .models import Patient, TreatmentPlan, Medication, FollowUpNote

User = get_user_model()


class TreatmentPlanModelTestCase(TestCase):
    """Test cases for TreatmentPlan model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testdoc',
            email='doc@test.com',
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            mrn='MRN001',
            full_name='John Doe',
            age=34,
            gender='M',
            created_by=self.user
        )
    
    def test_create_treatment_plan(self):
        """Test creating a treatment plan."""
        plan = TreatmentPlan.objects.create(
            patient=self.patient,
            title='Physical Therapy',
            description='Weekly PT sessions',
            start_date=date.today(),
            status='active',
            created_by=self.user
        )
        
        self.assertEqual(plan.title, 'Physical Therapy')
        self.assertEqual(plan.status, 'active')
        self.assertEqual(plan.patient, self.patient)
    
    def test_treatment_plan_status_choices(self):
        """Test treatment plan status choices."""
        plan = TreatmentPlan.objects.create(
            patient=self.patient,
            title='Test Plan',
            description='Test',
            start_date=date.today(),
            status='completed',
            created_by=self.user
        )
        
        self.assertIn(plan.status, ['active', 'completed', 'cancelled'])


class MedicationModelTestCase(TestCase):
    """Test cases for Medication model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testdoc',
            email='doc@test.com',
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            mrn='MRN001',
            full_name='John Doe',
            age=34,
            gender='M',
            created_by=self.user
        )
    
    def test_create_medication(self):
        """Test creating a medication record."""
        medication = Medication.objects.create(
            patient=self.patient,
            drug_name='Aspirin',
            dosage='100mg',
            frequency='Once daily',
            start_date=date.today(),
            prescribed_by=self.user
        )
        
        self.assertEqual(medication.drug_name, 'Aspirin')
        self.assertEqual(medication.patient, self.patient)
        self.assertEqual(medication.dosage, '100mg')


class TreatmentPlanAPITestCase(TestCase):
    """Test cases for TreatmentPlan API endpoints."""
    
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
            age=34,
            gender='M',
            created_by=self.user
        )
        
        self.plan = TreatmentPlan.objects.create(
            patient=self.patient,
            title='Physical Therapy',
            description='Weekly PT sessions',
            start_date=date.today(),
            status='active',
            created_by=self.user
        )
    
    def test_list_treatment_plans(self):
        """Test listing treatment plans for a patient."""
        response = self.client.get(f'/api/v1/patients/{self.patient.id}/treatments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)
    
    def test_create_treatment_plan(self):
        """Test creating a new treatment plan."""
        data = {
            'patient': self.patient.id,
            'title': 'Medication Plan',
            'description': 'Daily medication schedule',
            'start_date': str(date.today()),
            'status': 'active'
        }
        
        response = self.client.post('/api/v1/treatments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['title'], 'Medication Plan')
        self.assertEqual(TreatmentPlan.objects.count(), 2)
    
    def test_update_treatment_plan(self):
        """Test updating a treatment plan."""
        data = {
            'status': 'completed',
            'end_date': str(date.today())
        }
        
        response = self.client.patch(f'/api/v1/treatments/{self.plan.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.plan.refresh_from_db()
        self.assertEqual(self.plan.status, 'completed')
    
    def test_delete_treatment_plan(self):
        """Test deleting a treatment plan."""
        plan_id = self.plan.id
        response = self.client.delete(f'/api/v1/treatments/{plan_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TreatmentPlan.objects.filter(id=plan_id).exists())


class MedicationAPITestCase(TestCase):
    """Test cases for Medication API endpoints."""
    
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
            age=34,
            gender='M',
            created_by=self.user
        )
        
        self.medication = Medication.objects.create(
            patient=self.patient,
            drug_name='Aspirin',
            dosage='100mg',
            frequency='Once daily',
            start_date=date.today(),
            status='active',
            prescribed_by=self.user
        )
    
    def test_list_medications(self):
        """Test listing medications for a patient."""
        response = self.client.get(f'/api/v1/patients/{self.patient.id}/medications/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)
    
    def test_create_medication(self):
        """Test creating a new medication."""
        data = {
            'patient': self.patient.id,
            'drug_name': 'Ibuprofen',
            'dosage': '200mg',
            'frequency': 'Twice daily',
            'start_date': str(date.today()),
            'status': 'active'
        }
        
        response = self.client.post('/api/v1/medications/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['drug_name'], 'Ibuprofen')
        self.assertEqual(Medication.objects.count(), 2)
    
    def test_update_medication(self):
        """Test updating a medication."""
        data = {
            'status': 'discontinued',
            'end_date': str(date.today())
        }
        
        response = self.client.patch(f'/api/v1/medications/{self.medication.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.medication.refresh_from_db()
        self.assertEqual(self.medication.status, 'discontinued')
    
    def test_delete_medication(self):
        """Test deleting a medication."""
        med_id = self.medication.id
        response = self.client.delete(f'/api/v1/medications/{med_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Medication.objects.filter(id=med_id).exists())


class FollowUpNoteAPITestCase(TestCase):
    """Test cases for FollowUpNote API endpoints."""
    
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
            age=34,
            gender='M',
            created_by=self.user
        )
    
    def test_create_follow_up_note(self):
        """Test creating a follow-up note."""
        data = {
            'patient': self.patient.id,
            'title': 'Check-up Visit',
            'note': 'Patient is recovering well',
            'note_type': 'checkup'
        }
        
        response = self.client.post('/api/v1/follow-up-notes/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['title'], 'Check-up Visit')
        self.assertEqual(FollowUpNote.objects.count(), 1)
    
    def test_list_follow_up_notes(self):
        """Test listing follow-up notes for a patient."""
        FollowUpNote.objects.create(
            patient=self.patient,
            title='Note 1',
            note='Test note 1',
            note_type='checkup',
            created_by=self.user
        )
        FollowUpNote.objects.create(
            patient=self.patient,
            title='Note 2',
            note='Test note 2',
            note_type='progress',
            created_by=self.user
        )
        
        response = self.client.get(f'/api/v1/patients/{self.patient.id}/follow-up-notes/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 2)
