import uuid
from urllib.parse import quote

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from project.models import Project
from user.models import User

STATUS_CHOICES = (
    ("active", _("Active")),
    ("closed", _("Closed")),
)


class ChatRoom(models.Model):
    project = models.OneToOneField(Project, on_delete=models.SET_NULL, null=True)
    participants = models.ManyToManyField(User, related_name="chat_rooms")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active",
                              verbose_name=_("ChatRoom Status"))
    slug = models.SlugField(unique=True)
    modified_date = models.DateTimeField(auto_now=True, verbose_name=_("Modified Date"))
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())
        super(ChatRoom, self).save(*args, **kwargs)

    def __str__(self):
        if self.project:
            return str(_(f"Chat Room for {self.project.title}"))
        return str(_("Chat Room (No associated project)"))

    class Meta:
        verbose_name = _("Chat Room")
        verbose_name_plural = _("Chat Rooms")


class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def project_chat_file_path(self, filename):
        path = f"project_files/chat/{self.chat_room.slug}/{self.sender}/{filename}"
        path = path.replace("'", "_")
        path = quote(path)
        return path

    content = models.TextField(null=True, blank=True, verbose_name="Message")
    file = models.FileField(upload_to=project_chat_file_path, null=True, blank=True, verbose_name=_("File"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))

    def __str__(self):
        return str(_(f"Message from {self.sender} in {self.chat_room}"))

    def clean(self):
        if (self.sender not in self.chat_room.participants.all()) and not self.sender.is_admin:
            raise ValidationError(_("You are not a participant in this chat room."))

    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")


class MessageReceiver(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return str(self.receiver)

    class Meta:
        verbose_name = _("Message Receiver")
        verbose_name_plural = _("Message Receivers")
