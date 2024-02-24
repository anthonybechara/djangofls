from rest_framework import pagination


class ReviewPagination(pagination.PageNumberPagination):
    page_size = 5

