"""
Views for the Book APIs
"""
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework import (
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from book import serializers
from book.models import Book


@extend_schema(tags=["Book"])
class BookViewSet(viewsets.ModelViewSet):
    """View for manage book Api"""

    serializer_class = serializers.BookDetailSerializer
    queryset = Book.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return the serializer class for requests."""
        if self.action == "list":
            return serializers.BookSerializer

        return self.serializer_class

    def get_queryset(self):
        """Retrieve books for authenticated users."""
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def perform_create(self, serializer):
        """Save a new book for the authenticated user."""
        serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to a book"""
        book = self.get_object()
        serializer = serializers.BookImageSerializer(book, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
