from rest_framework import pagination


class ChatPagination(pagination.PageNumberPagination):
    page_size = 5
