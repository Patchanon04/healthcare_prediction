"""
WebSocket consumers for real-time chat.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat messages.
    URL: ws://domain/ws/chat/<room_id>/
    """
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Check if user is member of this room
        is_member = await self.check_room_membership()
        if not is_member:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        # Mark user online (short TTL to auto-expire)
        try:
            cache.set(f'user_online_{self.user.id}', True, timeout=120)
        except Exception:
            pass
        
        # Send user joined notification
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id,
                'username': self.user.username,
            }
        )
    
    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user_id': self.user.id,
                    'username': self.user.username,
                }
            )
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        try:
            cache.set(f'user_online_{self.user.id}', False, timeout=60)
        except Exception:
            pass
    
    async def receive(self, text_data):
        """Receive message from WebSocket."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                await self.handle_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read':
                await self.handle_read(data)
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def handle_message(self, data):
        """Handle new chat message."""
        content = data.get('content', '').strip()
        if not content:
            return
        
        # Save message to database
        message = await self.save_message(content)
        
        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': str(message.id),
                    'content': message.content,
                    'sender': await self.get_sender_payload(),
                    'created_at': message.created_at.isoformat(),
                }
            }
        )

        # Send notifications to other members of the room
        member_ids = await self.get_room_member_ids()
        room_name = await self.get_room_name()
        for uid in member_ids:
            if uid == self.user.id:
                continue
            await self.channel_layer.group_send(
                f'user_{uid}',
                {
                    'type': 'notify',
                    'room_id': str(self.room_id),
                    'room_name': room_name,
                    'sender': self.user.username,
                    'content': content,
                    'created_at': message.created_at.isoformat(),
                }
            )
    
    async def handle_typing(self, data):
        """Handle typing indicator."""
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': is_typing,
            }
        )
    
    async def handle_read(self, data):
        """Mark messages as read."""
        message_ids = data.get('message_ids', [])
        if message_ids:
            await self.mark_messages_read(message_ids)
            # Broadcast read receipts to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'user_id': self.user.id,
                    'message_ids': [str(mid) for mid in message_ids],
                }
            )
    
    # Handlers for different message types
    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }))
    
    async def user_joined(self, event):
        """Send user joined notification."""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'username': event['username'],
            }))
    
    async def user_left(self, event):
        """Send user left notification."""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'user_id': event['user_id'],
                'username': event['username'],
            }))
    
    async def user_typing(self, event):
        """Send typing indicator."""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing'],
            }))
    
    async def messages_read(self, event):
        """Forward read receipt events to clients."""
        # forward to everyone (sender will use it to toggle read checks)
        await self.send(text_data=json.dumps({
            'type': 'read',
            'user_id': event['user_id'],
            'message_ids': event['message_ids'],
        }))
    
    # Database operations
    @database_sync_to_async
    def check_room_membership(self):
        """Check if user is a member of the room."""
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return room.members.filter(id=self.user.id).exists()
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        """Save message to database."""
        room = ChatRoom.objects.get(id=self.room_id)
        message = Message.objects.create(
            room=room,
            sender=self.user,
            content=content
        )
        # Update room's updated_at
        room.save()
        return message
    
    @database_sync_to_async
    def get_sender_payload(self):
        """Safely build sender payload in sync context (may touch DB via user.profile)."""
        full_name = ''
        avatar_url = ''
        try:
            profile = getattr(self.user, 'profile', None)
            if profile and getattr(profile, 'full_name', None):
                full_name = profile.full_name
            # avatar may be ImageField/FileField, get url if available
            if profile and getattr(profile, 'avatar', None):
                try:
                    if profile.avatar:
                        avatar_url = getattr(profile.avatar, 'url', '') or str(profile.avatar)
                except Exception:
                    avatar_url = ''
        except Exception:
            full_name = ''
        return {
            'id': self.user.id,
            'username': self.user.username,
            'full_name': full_name,
            'avatar': avatar_url,
        }

    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        """Mark messages as read by current user."""
        messages = Message.objects.filter(id__in=message_ids, room_id=self.room_id)
        for msg in messages:
            msg.read_by.add(self.user)

    @database_sync_to_async
    def get_room_member_ids(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return list(room.members.values_list('id', flat=True))
        except ChatRoom.DoesNotExist:
            return []

    @database_sync_to_async
    def get_room_name(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            if room.name:
                return room.name
            # Fallback: generate name from members
            members = room.members.exclude(id=self.user.id)
            names = [getattr(m, 'username', 'User') for m in members[:2]]
            return ', '.join(names) if names else 'Chat'
        except ChatRoom.DoesNotExist:
            return 'Chat'


class NotificationConsumer(AsyncWebsocketConsumer):
    """User-level notification channel. Group name: user_<user_id>."""
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        try:
            cache.set(f'user_online_{self.user.id}', True, timeout=120)
        except Exception:
            pass

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        try:
            cache.set(f'user_online_{self.user.id}', False, timeout=60)
        except Exception:
            pass

    async def notify(self, event):
        # Forward notification (chat or second opinion) to client unchanged
        payload = {k: v for k, v in event.items() if k != 'type'}
        payload['type'] = 'notification'
        await self.send(text_data=json.dumps(payload))
