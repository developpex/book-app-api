from django_filters import rest_framework as filters

from book.models import Book


class BookFilter(filters.FilterSet):
    genres = filters.CharFilter(method="filter_genres")
    authors = filters.CharFilter(method="filter_authors")

    class Meta:
        model = Book
        fields = ['genres', 'authors']

    def filter_genres(self, queryset, name, value):
        genre_names = value.split(',')
        return queryset.filter(genres__name__in=genre_names).distinct()

    def filter_authors(self, queryset, name, value):
        author_names = value.split(',')
        return queryset.filter(authors__name__in=author_names).distinct()
