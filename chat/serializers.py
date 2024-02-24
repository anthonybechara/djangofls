from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import Base64FileField
import filetype

from rest_framework import serializers

from chat.models import ChatRoom, Message
from user.models import User


def get_participant(instance, request):
    participants_info = []

    for participant in instance.participants.all():
        user_profile = participant.userprofile
        profile_picture_url = request.build_absolute_uri(user_profile.profile_picture.url)

        participant_info = {
            "username": participant.username,
            "photo_url": profile_picture_url,
        }
        participants_info.append(participant_info)

    return participants_info


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username",)


class FileField(Base64FileField):
    ALLOWED_TYPES = [
        # Image
        "dwg", "xcf", "jpg", "jpx", "png", "apng", "gif", "webp", "cr2", "tif", "bmp", "jxr", "psd", "ico", "heic",
        "avif",
        # Video
        "3gp", "mp4", "m4v", "mkv", "webm", "mov", "avi", "wmv", "mpg", "flv",
        # Audio
        "aac", "mid", "mp3", "m4a", "ogg", "flac", "wav", "amr", "aiff",
        # Archive
        "br", "rpm", "dcm", "epub", "zip", "tar", "rar", "gz", "bz2", "7z", "xz", "pdf", "exe", "swf", "rtf", "eot",
        "ps", "sqlite", "nes", "crx", "cab", "deb", "ar", "Z", "lzo", "lz", "lz4", "zstd",
        # Document
        "doc", "docx", "odt", "xls", "xlsx", "ods", "ppt", "pptx", "odp",
        # Font
        "woff", "woff2", "ttf", "otf",
        # Application
        "wasm"
    ]

    def get_file_extension(self, filename, decoded_file):
        kind = filetype.guess_extension(decoded_file)
        return kind

    def to_internal_value(self, data):
        if isinstance(data, str):
            return super().to_internal_value(data)
        return data


class MessageSerializer(serializers.ModelSerializer):
    chat_room = serializers.StringRelatedField()
    sender = UserSerializer(read_only=True)
    file = FileField(required=False)

    class Meta:
        model = Message
        fields = "__all__"


class ChatRoomSerializer(serializers.ModelSerializer):
    chats_url = serializers.HyperlinkedIdentityField(view_name="chat-message", lookup_field="slug")
    project_name = serializers.SerializerMethodField()
    status = serializers.StringRelatedField()
    participants_info = serializers.SerializerMethodField(read_only=True, label=_("Participants Information"))

    class Meta:
        model = ChatRoom
        fields = "__all__"

    @staticmethod
    def get_project_name(instance):
        project = instance.project
        if project:
            return project.title
        return None

    def get_participants_info(self, instance):
        return get_participant(instance, self.context["request"])
