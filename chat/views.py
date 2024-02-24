from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, F
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _

from rest_framework import mixins, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from chat.models import ChatRoom, Message
from chat.pagination import ChatPagination
from chat.permissions import IsParticipantAndClosedPermission
from chat.serializers import ChatRoomSerializer, MessageSerializer


class ChatRoomView(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["project__title", "=participants__username"]
    lookup_field = "slug"
    pagination_class = ChatPagination

    def get_queryset(self):
        user = self.request.user
        queryset = ChatRoom.objects.all()

        if user.is_admin and self.action == "list":
            queryset = queryset.filter(status="active")
        elif self.action == "list":
            queryset = queryset.filter(participants=user, status="active")

        queryset = queryset.annotate(last_message_timestamp=Coalesce(Max("messages__timestamp"), F("created")))
        queryset = queryset.order_by("-last_message_timestamp", "-created")

        return queryset

    def get_permissions(self):
        if self.action == "message":
            self.permission_classes = [IsAuthenticated, IsParticipantAndClosedPermission]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "closed_chat":
            return ChatRoomSerializer
        elif self.action == "message":
            return MessageSerializer
        return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if user not in instance.participants.all() and not user.is_admin:
            return Response({"error": "You are not a participant in this chatroom."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def closed_chat(self, request):
        user = self.request.user
        if user.is_admin:
            closed_proposals = ChatRoom.objects.filter(status="closed").order_by("-modified_date")
        else:
            closed_proposals = ChatRoom.objects.filter(participants=user, status="closed").order_by("-modified_date")

        closed_proposals = self.filter_queryset(closed_proposals)

        page = self.paginate_queryset(closed_proposals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(closed_proposals, many=True)
            return Response(serializer.data)

    @action(detail=True, methods=["get", "post"])
    def message(self, request, slug=None):
        chatroom = self.get_object()
        if request.method == "GET":
            try:
                try:
                    chosen_proposal_time = chatroom.project.chosenproposal.chosen_date
                    published_user = chatroom.project.published_user
                except ObjectDoesNotExist:
                    chosen_proposal_time = None
                    published_user = None

                if chosen_proposal_time and self.request.user != published_user:
                    message_room = Message.objects.filter(chat_room=chatroom,
                                                          timestamp__gte=chosen_proposal_time).order_by("-timestamp")
                else:
                    message_room = Message.objects.filter(chat_room=chatroom).order_by("-timestamp")

                page = self.paginate_queryset(message_room)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                else:
                    serializer = self.get_serializer(message_room, many=True)
                    return Response(serializer.data)
            except ChatRoom.DoesNotExist:
                return Response({"error": _("Chatroom not found")}, status=status.HTTP_404_NOT_FOUND)

        ########################################################################################################################
        elif request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                file = serializer.validated_data.get("file")
                content = serializer.validated_data.get("content")
                if not file and not content:
                    return Response({"error": _("No message provided")}, status=status.HTTP_400_BAD_REQUEST)
                serializer.save(sender=request.user, chat_room=chatroom, file=file)
                return Response({"message": _("Message sent successfully"), "data": serializer.data},
                                status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
