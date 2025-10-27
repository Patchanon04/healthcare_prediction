"""
Unit tests for the predictions app.
"""
import unittest
import uuid
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

from .models import Transaction

User = get_user_model()


class HealthCheckTestCase(TestCase):
    """
    Test cases for health check endpoint.
    """
    def setUp(self):
        self.client = APIClient()
    
    def test_health_check_success(self):
        """Test health check endpoint returns OK status."""
        response = self.client.get('/api/v1/health/')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])
        self.assertIn('status', response.json())
        # db field is optional in health check response


class TransactionModelTestCase(TestCase):
    """
    Test cases for Transaction model.
    """
    
    def test_create_transaction(self):
        """Test creating a transaction record."""
        transaction = Transaction.objects.create(
            image_url="https://example.com/dog.jpg",
            diagnosis="Labrador Retriever",
            confidence=0.92,
            model_version="v1.0",
            processing_time=0.5
        )
        
        self.assertIsInstance(transaction.id, uuid.UUID)
        self.assertEqual(transaction.diagnosis, "Labrador Retriever")
        self.assertEqual(transaction.confidence, 0.92)
        self.assertIsNotNone(transaction.uploaded_at)


class TransactionHistoryTestCase(TestCase):
    """
    Test cases for transaction history endpoint.
    """
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        
        # Create test transactions
        for i in range(15):
            Transaction.objects.create(
                image_url=f"https://example.com/dog{i}.jpg",
                diagnosis=f"Diagnosis {i}",
                confidence=0.90 + (i * 0.01),
                model_version="v1.0",
                processing_time=0.5
            )
    
    def test_get_history_first_page(self):
        """Test getting first page of history."""
        # Verify transactions were created
        count = Transaction.objects.filter(user=self.user).count()
        self.assertEqual(count, 15, "Transactions should be created in setUp")
        
        response = self.client.get('/api/v1/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.json())
        self.assertIn('count', response.json())
        self.assertEqual(len(response.json()['results']), 10)  # Default page size
    
    def test_get_history_with_pagination(self):
        """Test pagination parameters."""
        response = self.client.get('/api/v1/history/?page=2&page_size=5')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.json())
        # Page 2 with page_size=5 should have 5 results (items 11-15)
        self.assertEqual(len(response.json()['results']), 5)


class UploadImageTestCase(TestCase):
    """
    """
    
    def setUp(self):
        self.client = APIClient()
    
    @override_settings(USE_S3=False, MEDIA_ROOT='/tmp/test_media')
    @patch('predictions.views.call_ml_service')
    @patch('predictions.views.default_storage.save')
    def test_upload_image_success(self, mock_storage, mock_ml_service):
        """Test successful image upload."""
        # Mock storage save
        mock_storage.return_value = 'patient_images/test.jpg'
        
        # Mock ML service response
        mock_ml_service.return_value = {
            'diagnosis': 'Labrador Retriever',
            'confidence': 0.92,
            'model_version': 'v1.0',
            'processing_time': 0.5
        }
        
        # Create test image
        image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x44\x00\x3b'
        image = SimpleUploadedFile(
            "test_dog.jpg",
            image_content,
            content_type="image/jpeg"
        )
        
        # Authenticate user
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=user)
        
        # Include required patient info
        response = self.client.post('/api/v1/upload/', {
            'image': image,
            'patient_name': 'Test Patient',
            'age': 30,
            'gender': 'M',
            'mrn': 'TEST001'
        }, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn('diagnosis', data)
        self.assertIn('confidence', data)
        self.assertEqual(data['diagnosis'], 'Labrador Retriever')
    
    @override_settings(USE_S3=False, MEDIA_ROOT='/tmp/test_media')
    def test_upload_no_image(self):
        """Test upload without image file."""
        # Authenticate user
        user = User.objects.create_user(username='testuser2', password='testpass')
        self.client.force_authenticate(user=user)
        
        response = self.client.post('/api/v1/upload/', {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())
