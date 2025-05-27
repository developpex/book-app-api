"""
Serializers for book APIs
"""

from rest_framework import serializers

from book.models import Book
from catalog.models import Genre, Author
from catalog.serializers import GenreSerializer, AuthorSerializer


class BookSerializer(serializers.ModelSerializer):
    """Serializer for books."""
    genres = GenreSerializer(many=True, required=False)
    authors = AuthorSerializer(many=True, required=False)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "price",
            "link",
            "genres",
            "authors"
        ]
        read_only_fields = ["id"]

    def _get_or_create_genres(self, genres, book):
        """Handle getting or creating genres"""
        for genre in genres:
            name = genre["name"].strip().title()
            genre_object, _ = Genre.objects.get_or_create(
                name__iexact=name,
                defaults={"name": name}
            )
            book.genres.add(genre_object)

    def _get_or_create_authors(self, authors, book):
        for author in authors:
            name = author["name"].strip().title()
            author_obj, _ = Author.objects.get_or_create(
                name__iexact=name,
                defaults={"name": name}
            )
            book.authors.add(author_obj)

    def create(self, validated_data):
        """Create a book."""
        genres = validated_data.pop("genres", [])
        authors = validated_data.pop("authors", [])
        book = Book.objects.create(**validated_data)
        self._get_or_create_genres(genres, book)
        self._get_or_create_authors(authors, book)
        return book

    def update(self, instance, validated_data):
        """Update a book."""
        genres = validated_data.pop("genres", None)
        if genres is not None:
            instance.genres.clear()
            self._get_or_create_genres(genres, instance)

        authors = validated_data.pop("authors", None)
        if authors is not None:
            instance.authors.clear()
            self._get_or_create_authors(authors, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class BookDetailSerializer(BookSerializer):
    """Serializer for book detail view"""

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + ["description"]
