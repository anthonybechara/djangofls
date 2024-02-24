from django_filters.rest_framework import DjangoFilterBackend, ChoiceFilter
from rest_framework import filters


class TransactionFilterBackend(DjangoFilterBackend):
    def get_filterset_class(self, view, queryset=None):
        filterset_class = super().get_filterset_class(view, queryset)
        user = view.request.user

        class TransactionFilter(filterset_class):
            transaction_type = ChoiceFilter(
                choices=(
                    [(choice[0], choice[1]) for choice in filterset_class.Meta.model.TRANSACTION_CHOICES]
                    if user.is_superuser
                    else [(choice[0], choice[1]) for choice in filterset_class.Meta.model.TRANSACTION_CHOICES if
                          not choice[0].startswith("SUPER")]
                )
            )

        return TransactionFilter


class ExactWordSearchFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_param = self.get_search_terms(request)
        if search_param:
            word_regex = r"\b{}\b".format(search_param[0])
            return queryset.filter(description__iregex=word_regex)
        return queryset
