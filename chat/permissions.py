from rest_framework import permissions
from django.utils.translation import gettext as _
from rest_framework.exceptions import NotFound


class IsParticipantAndClosedPermission(permissions.BasePermission):
    message = _("Chatroom is closed, You cannot send Messages")

    def has_permission(self, request, view):
        chat_room = view.get_object()
        is_participant = request.user in chat_room.participants.all() or request.user.is_admin
        if not is_participant:
            raise NotFound(_("You are not a participant in this chatroom."))
        is_chatroom_closed = chat_room.status == "closed"
        return (is_participant and not (request.method == "POST" and is_chatroom_closed)) or request.user.is_admin
