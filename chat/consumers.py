import json
from channels.generic.websocket import AsyncWebsocketConsumer #type:ignore
from channels.db import database_sync_to_async #type:ignore
import logging
from django.contrib.auth.models import User
from .models import ChatSession, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real time chat.
    each instance of consumer handles a specific chat session's connection
    """
    # Get an instance of a logger
    logger = logging.getLogger(__name__)

    async def connect(self):
        """
        called when a WebSocket connection is attempted.
        authenticates the user, checks if they are a participant in the chat session,
        and if so, adds their connection to the chat room group and accepts the WebSocket connection.
        """
        #exctract session_id
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        #define unique group name
        self.chat_room_group_name = f'chat_{self.session_id}'
        #get user from the connection scope (populated by AuthMiddlewareStack)
        self.user = self.scope['user']

        #reject connection if user is not authenticated
        if not self.user.is_authenticated:
            await self.close()
            return

        # Check if the user is part of this chat session
        is_participant = await self.is_user_participant(self.user, self.session_id)
        if not is_participant:
            await self.close() # Close connection if user is not part of the session
            return

        #add the user's channel to the channel layer group for this chat room
        await self.channel_layer.group_add(
            self.chat_room_group_name,
            self.channel_name
        )
        #accept connection
        await self.accept()

    async def disconnect(self, close_code):
        """
        called when WebSocket connection is closed.
        remove user's channel from chat room group.
        """
        if hasattr(self, 'chat_room_group_name'): # Ensure it was set
            await self.channel_layer.group_discard(
                self.chat_room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        called when a message is recieved.
        parse the message, save it to the database, broadcast it to the chat room.
        """
        try:
            text_data_json = json.loads(text_data)
            message_content = text_data_json['message']
            sender_username = self.user.username

            self.logger.info(f"Received message: '{message_content}' from {sender_username} for session {self.session_id}")

            # Save message to database
            chat_message = await self.save_message(self.session_id, self.user, message_content)
            self.logger.info(f"Message from {sender_username} saved to DB with ID: {chat_message.id}")

            # Send message to room group
            await self.channel_layer.group_send(
                self.chat_room_group_name,
                {
                    'type': 'chat_message', # This will call the chat_message method
                    'message': message_content,
                    'sender_username': sender_username,
                    'timestamp': chat_message.timestamp.isoformat()
                }
            )
            self.logger.info(f"Message from {sender_username} broadcasted to group {self.chat_room_group_name}")

        except json.JSONDecodeError:
            self.logger.error(f"Failed to decode JSON from WebSocket: {text_data}")
        except KeyError:
            self.logger.error(f"Received JSON without 'message' key: {text_data}")
        except Exception as e:
            # Log any other exceptions, which is crucial for debugging async code
            self.logger.error(f"An unexpected error occurred in receive method for session {self.session_id}: {e}", exc_info=True)

    async def chat_message(self, event):
        """
        Handler for messages received from the channel layer group (i.e., broadcasted messages).
        Sends the message data down to the client's WebSocket.
        The 'type' in group_send corresponds to this method name.
        """
        message = event['message']
        sender_username = event['sender_username']
        timestamp = event['timestamp']

        # Send message data to connected client via WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_username': sender_username,
            'timestamp': timestamp
        }))

    @database_sync_to_async
    def is_user_participant(self, user, session_id):
        """
        Asynchronously checks if the given user is a participant (buyer or seller)
        in the chat session identified by session_id.
        """
        try:
            session = ChatSession.objects.get(id=session_id)
            return user == session.buyer or user == session.seller
        except ChatSession.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, session_id, sender, content):
        """
        Asynchronously saves a new chat message to the database.
        Associates the message with the given session_id and sender.
        """
        session = ChatSession.objects.get(id=session_id)
        chat_message = ChatMessage.objects.create(session=session, sender=sender, content=content)
        # The ChatMessage model's save method already updates session.updated_at
        return chat_message
