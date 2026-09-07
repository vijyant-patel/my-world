"""
Search and filter backends for books and summaries.
"""
import django_filters
from django.db.models import Q
from .models import Book, Summary


class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    author = django_filters.CharFilter(lookup_expr="icontains")
    category = django_filters.CharFilter(field_name="category__slug")
    status = django_filters.ChoiceFilter(choices=Book.STATUS_CHOICES)
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Book
        fields = ["title", "author", "isbn", "category", "status"]

    def filter_search(self, qs, name, value):
        if not value:
            return qs
        return qs.filter(Q(title__icontains=value) | Q(author__icontains=value))


class BookSummaryFilter(django_filters.FilterSet):
    book = django_filters.NumberFilter(field_name="book_id")
    summary_type = django_filters.CharFilter(field_name="summary_type")
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Summary
        fields = ["book", "summary_type", "is_public"]

    def filter_search(self, qs, name, value):
        if not value:
            return qs
        return qs.filter(is_public=True).filter(
            Q(content__icontains=value)
            | Q(quick_preview__icontains=value)
            | Q(key_takeaways__icontains=value)
            | Q(book__title__icontains=value)
        )
