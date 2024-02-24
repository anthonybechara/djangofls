import base64
import uuid

import filetype
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from chat.models import Message, ChatRoom, MessageReceiver
from django.utils.timesince import timesince
import json

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        if not await self.is_participant(self.room_name, self.scope["user"]):
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.change_message_status(self.scope["user"], self.room_name)

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        type = data.get("type")
        username = str(self.scope["user"])
        content = data.get("content")
        file = data.get("file")
        chat_room = self.room_name

        if type == "message":
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "chat_message",
                    "content": content,
                    "file": file,
                    "username": username,
                    "chat_room": chat_room,
                }
            )

        elif type in ["typing", "not-typing"]:
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "writing_active" if type == "typing" else "writing_inactive",
                    "content": content,
                    "username": username,
                    "chat_room": chat_room,
                }
            )

        if type == "mark_as_read":
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "update_message_status",
                    "username": username,
                    "chat_room": chat_room,
                    "is_seen": True,
                }
            )

    async def update_message_status(self, event):
        # print("content status", event)
        username = event["username"]
        chat_room = event["chat_room"]
        is_seen = await self.change_message_status(username, chat_room)
        await self.send(text_data=json.dumps({
            "username": username,
            "chat_room": chat_room,
            "is_seen": is_seen,
        }))

    async def chat_message(self, event):
        # print("chat_message", event)
        username = event["username"]
        chat_room = event["chat_room"]
        content = event["content"]
        file_data = event["file"]

        if not content and not file_data:
            error_message = {"error": "Message should contain either content or a file."}
            await self.send(text_data=json.dumps(error_message))
            return {"error": error_message}

        first_name, last_name = await self.get_first_name_and_last_name(username)
        participants_count = await self.get_participants_count(chat_room)
        receivers = await self.get_receivers(chat_room, username)

        uploaded_file, file_name = self.decode_base64_and_save_file(file_data)

        if uploaded_file == file_name == 1:
            error_message = {"error": "Unsupported file type."}
            await self.send(text_data=json.dumps(error_message))
            return {"error": error_message}

        new_message = await self.save_message(username, chat_room, receivers, content, uploaded_file)

        await self.send(text_data=json.dumps({
            **event,
            "participants": participants_count,
            "first_name": first_name,
            "last_name": last_name,
            "timestamp": timesince(new_message.timestamp),
        }))

    async def writing_active(self, event):
        # print("active", event)
        username = event["username"]
        first_name, last_name = await self.get_first_name_and_last_name(username)
        await self.send(text_data=json.dumps({
            **event,
            "first_name": first_name,
            "last_name": last_name,
        }))

    async def writing_inactive(self, event):
        # print("inactive", event)
        await self.send(text_data=json.dumps({
            **event,
        }))

    @staticmethod
    def decode_base64_and_save_file(file_data):
        if not file_data:
            return None, None

        file = base64.b64decode(file_data)
        kind = filetype.guess_extension(file)

        if not kind:
            return 1, 1

        file_extension = f".{kind}" if kind else ".bin"
        file_name = f"{str(uuid.uuid4())}{file_extension}"

        uploaded_file = SimpleUploadedFile(file_name, file,
                                           content_type=kind.mime if kind else "application/octet-stream")
        return uploaded_file, file_name

    @database_sync_to_async
    def is_participant(self, chat_room, user):
        chatroom = ChatRoom.objects.get(slug=chat_room)
        return ((user in chatroom.participants.all()) or user.is_admin) and chatroom.status == "active"

    @database_sync_to_async
    def save_message(self, username, chat_room, receivers, content=None, file=None):
        user = User.objects.get(username=username)
        chat_room = ChatRoom.objects.get(slug=chat_room)
        new_message = Message.objects.create(chat_room=chat_room, sender=user, content=content, file=file)
        receiver_users = User.objects.filter(username__in=receivers)
        for receiver in receiver_users:
            MessageReceiver.objects.create(message=new_message, receiver=receiver, is_seen=False)
        return new_message

    @database_sync_to_async
    def get_first_name_and_last_name(self, username):
        user = User.objects.get(username=username)
        return user.first_name, user.last_name

    @database_sync_to_async
    def get_participants_count(self, room_name):
        room_instance = ChatRoom.objects.get(slug=room_name)
        return room_instance.participants.count()

    @database_sync_to_async
    def get_receivers(self, room_name, username):
        user = User.objects.get(username=username)
        room_instance = ChatRoom.objects.get(slug=room_name)
        receivers = room_instance.participants.exclude(username=user)
        usernames = [receiver.username for receiver in receivers]
        return usernames

    @database_sync_to_async
    def change_message_status(self, username, chat_room):
        user = User.objects.get(username=username)
        room_name = ChatRoom.objects.get(slug=chat_room)
        if user in room_name.participants.all():
            message_receivers = MessageReceiver.objects.filter(message__chat_room=room_name, receiver=user)
            for message_receiver in message_receivers:
                message_receiver.is_seen = True
                message_receiver.save()
