"""
Unit tests for Chat and WebSocket functionality.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import re_path

from .models import ChatRoom, Message

User = get_user_model()


class ChatRoomModelTestCase(TestCase):
    """Test cases for ChatRoom model."""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
    
    def test_create_chat_room(self):
        """Test creating a chat room."""
        room = ChatRoom.objects.create(
            name='Test Room',
            created_by=self.user1
        )
        room.members.add(self.user1, self.user2)
        
        self.assertEqual(room.name, 'Test Room')
        self.assertEqual(room.members.count(), 2)
        self.assertIn(self.user1, room.members.all())
        self.assertIn(self.user2, room.members.all())
    
    def test_chat_room_str(self):
        """Test string representation of chat room."""
        room = ChatRoom.objects.create(
            name='Test Room',
            created_by=self.user1
        )
        
        self.assertEqual(str(room), 'Test Room')


class MessageModelTestCase(TestCase):
    """Test cases for Message model."""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        self.room = ChatRoom.objects.create(
            name='Test Room',
            created_by=self.user1
        )
        self.room.members.add(self.user1, self.user2)
    
    def test_create_message(self):
        """Test creating a chat message."""
        message = Message.objects.create(
            room=self.room,
            sender=self.user1,
            content='Hello, World!'
        )
        
        self.assertEqual(message.content, 'Hello, World!')
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.read_by.count(), 0)
    
    def test_mark_message_as_read(self):
        """Test marking message as read."""
        message = Message.objects.create(
            room=self.room,
            sender=self.user1,
            content='Test message'
        )
        
        message.read_by.add(self.user2)
        
        self.assertIn(self.user2, message.read_by.all())


class ChatRoomAPITestCase(TestCase):
    """Test cases for ChatRoom API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user1)
        
        # Create test room
        self.room = ChatRoom.objects.create(
            name='Test Room',
            created_by=self.user1
        )
        self.room.members.add(self.user1, self.user2)
    
    def test_list_chat_rooms(self):
        """Test listing chat rooms."""
        response = self.client.get('/api/v1/chat/rooms/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.json())
        self.assertGreaterEqual(len(response.json()['results']), 1)
    
    def test_get_chat_room_detail(self):
        """Test getting chat room detail."""
        response = self.client.get(f'/api/v1/chat/rooms/{self.room.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['name'], 'Test Room')
        self.assertIn('members', data)
    
    def test_create_chat_room(self):
        """Test creating a new chat room."""
        data = {
            'name': 'New Room',
            'members': [self.user1.id, self.user2.id]
        }
        
        response = self.client.post('/api/v1/chat/rooms/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['name'], 'New Room')
        self.assertEqual(ChatRoom.objects.count(), 2)
    
    def test_list_messages(self):
        """Test listing messages in a room."""
        # Create test messages
        Message.objects.create(
            room=self.room,
            sender=self.user1,
            content='Message 1'
        )
        Message.objects.create(
            room=self.room,
            sender=self.user2,
            content='Message 2'
        )
        
        response = self.client.get(f'/api/v1/chat/rooms/{self.room.id}/messages/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.json())
        self.assertGreaterEqual(len(response.json()['results']), 2)
    
    def test_send_message(self):
        """Test sending a message."""
        data = {
            'content': 'Hello from test!'
        }
        
        response = self.client.post(f'/api/v1/chat/rooms/{self.room.id}/messages/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['content'], 'Hello from test!')
        self.assertEqual(Message.objects.count(), 1)
    
    def test_mark_messages_as_read(self):
        """Test marking messages as read."""
        message = Message.objects.create(
            room=self.room,
            sender=self.user2,
            content='Unread message'
        )
        
        data = {
            'message_ids': [message.id]
        }
        
        response = self.client.post(f'/api/v1/chat/rooms/{self.room.id}/read/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        message.refresh_from_db()
        self.assertIn(self.user1, message.read_by.all())
    
    def test_get_unread_count(self):
        """Test getting unread message count."""
        # Create unread messages
        Message.objects.create(
            room=self.room,
            sender=self.user2,
            content='Unread 1'
        )
        Message.objects.create(
            room=self.room,
            sender=self.user2,
            content='Unread 2'
        )
        
        response = self.client.get('/api/v1/chat/unread-count/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('unread_count', response.json())
        self.assertGreaterEqual(response.json()['unread_count'], 2)
    
    def test_unauthorized_access(self):
        """Test that unauthenticated users cannot access chat."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/chat/rooms/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_cannot_access_other_rooms(self):
        """Test that users can only access rooms they're members of."""
        user3 = User.objects.create_user(
            username='user3',
            email='user3@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user3)
        
        response = self.client.get(f'/api/v1/chat/rooms/{self.room.id}/')
        
        # Should return 404 or 403
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


class ChatUsersAPITestCase(TestCase):
    """Test cases for Chat Users API."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create additional users
        User.objects.create_user(username='user2', email='user2@test.com', password='pass')
        User.objects.create_user(username='user3', email='user3@test.com', password='pass')
    
    def test_list_chat_users(self):
        """Test listing available users for chat."""
        response = self.client.get('/api/v1/chat/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return all users except the current user
        self.assertGreaterEqual(len(response.json()), 2)
