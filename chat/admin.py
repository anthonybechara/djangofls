from django.contrib import admin

from chat.models import ChatRoom, Message, MessageReceiver


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "status")
    filter_horizontal = ("participants",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat_room", "sender", "timestamp")


@admin.register(MessageReceiver)
class MessageReceiverAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "receiver", "is_seen")
