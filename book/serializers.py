"""
Serializers for book APIs
"""

from rest_framework import serializers

from book.models import (
    Book
)


class BookSerializer(serializers.ModelSerializer):
    """Serializer for books."""

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "price",
            "link",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        """Create a recipe."""
        book = Book.objects.create(**validated_data)
        return book


class BookDetailSerializer(BookSerializer):
    """Serializer for book detail view"""

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + ["description"]
