"""
Serializers for book APIs
"""

from rest_framework import serializers

from book.models import Book
from catalog.models import Genre
from catalog.serializers import GenreSerializer


class BookSerializer(serializers.ModelSerializer):
    """Serializer for books."""
    genres = GenreSerializer(many=True, required=False)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "price",
            "link",
            "genres"
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

    def create(self, validated_data):
        """Create a book."""
        genres = validated_data.pop("genres", [])
        book = Book.objects.create(**validated_data)
        self._get_or_create_genres(genres, book)
        return book

    def update(self, instance, validated_data):
        """Update a book."""
        genres = validated_data.pop("genres", None)
        if genres is not None:
            instance.genres.clear()
            self._get_or_create_genres(genres, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class BookDetailSerializer(BookSerializer):
    """Serializer for book detail view"""

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + ["description"]
