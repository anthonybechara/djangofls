from rest_framework import pagination


class TransactionLogPagination(pagination.PageNumberPagination):
    page_size = 10
