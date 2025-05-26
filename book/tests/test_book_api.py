"""
Tests for book APIs
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.serializers import (
    BookSerializer
)
from core.models import (
    Book
)

BOOK_URL = reverse("book:book-list")


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


def detail_url(book_id):
    """Create and return a book detail URL."""
    return reverse("book:book-detail", args=[book_id])


def create_book(user, **params):
    """Create and return a book"""
    defaults = {
        "title": "Sample book title",
        "price": Decimal("5.25"),
        "description": "Sample book description",
        "link": "http://example.com/book.pdf"
    }
    defaults.update(params)

    book = Book.objects.create(user=user, **defaults)
    return book


class PublicBookAPITests(TestCase):
    """Test unauthenticated API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBookAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="user@example.com",
            password="userpass123"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_book(self):
        create_book(user=self.user)
        create_book(user=self.user)

        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        books = Book.objects.all().order_by("-id")
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.data, serializer.data)
