from rest_framework import permissions
from django.utils.translation import gettext as _

from user_resume.models import PortfolioFile


class CurrentUser(permissions.IsAuthenticated):
    message = _("You dont have access to perform this action.")

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class PortfolioFileDelete(permissions.IsAuthenticated):
    message = _("You dont have permission to delete this file")

    def has_permission(self, request, view):
        file = view.get_object()
        if isinstance(file, PortfolioFile):
            p_work = file.portfolio_work
            return request.user == p_work.user or request.user.is_admin
        return False


# class CanReview(permissions.IsAuthenticated):
#     def has_object_permission(self, request, view, obj):
#         chat_room = obj
#         is_participant = request.user in chat_room.participants.all()
#         is_chatroom_closed = chat_room.status == 'closed'
#         return is_participant and not (request.method == 'POST' and is_chatroom_closed)
