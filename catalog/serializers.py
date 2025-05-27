"""
Serializers for catalog APIs
"""

from rest_framework import serializers

from catalog.models import Genre, Author


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for Genres."""

    class Meta:
        model = Genre
        fields = ["id", "name"]
        read_only_fields = ["id"]


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Authors."""

    class Meta:
        model = Author
        fields = ["id", "name"]
        read_only_fields = ["id"]
