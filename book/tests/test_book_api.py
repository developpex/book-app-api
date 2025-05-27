"""
Tests for book APIs
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import (
    Book
)
from book.serializers import (
    BookSerializer, BookDetailSerializer
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
        """Test retrieving a list of books"""
        create_book(user=self.user)
        create_book(user=self.user)

        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        books = Book.objects.all().order_by("-id")
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_book_list_limited_to_user(self):
        """Test list of books is limited to authenticated user."""
        new_user = create_user(
            email="newuser@example.com",
            password="testpass123"
        )

        create_book(user=self.user)
        create_book(user=new_user)

        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        books = Book.objects.filter(user=self.user)
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_get_book_detail(self):
        """Test get book detail"""
        book = create_book(self.user)

        url = detail_url(book.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = BookDetailSerializer(book)
        self.assertEqual(res.data, serializer.data)

    def test_create_book(self):
        """Test creating a book"""
        payload = {
            "title": "Sample book",
            "price": Decimal("5.99"),
            "link": "https://example.com/book.pdf"
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=res.data["id"])
        for key, value in payload.items():
            self.assertEqual(getattr(book, key), value)
        self.assertEqual(book.user, self.user)

    def test_partial_update(self):
        """Test the partial update of a book"""
        original_link = "https://example.com/book.pdf"
        book = create_book(
            user=self.user,
            title="Sample book title",
            link=original_link
        )

        payload = {
            "title": "New book title"
        }
        url = detail_url(book.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        self.assertEqual(book.title, payload["title"])
        self.assertEqual(book.link, original_link)
        self.assertEqual(book.user, self.user)

    def test_full_update(self):
        """Test full update of book."""
        book = create_book(
            user=self.user,
            title="Sample book title",
            link="https://exmaple.com/book.pdf",
            description="Sample book description.",
        )

        payload = {
            "title": "New book title",
            "link": "https://example.com/new-book.pdf",
            "description": "New book description",
            "price": Decimal("2.50"),
        }
        url = detail_url(book.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(book, key), value)
        self.assertEqual(book.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the book user results in an error."""
        new_user = create_user(email="user2@example.com", password="test123")
        book = create_book(user=self.user)

        payload = {"user": new_user.id}
        url = detail_url(book.id)
        self.client.patch(url, payload)

        book.refresh_from_db()
        self.assertEqual(book.user, self.user)

    def test_delete_book(self):
        """Test deleting a book successful."""
        book = create_book(user=self.user)

        url = detail_url(book.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Book.objects.filter(id=book.id).exists())

    def test_book_other_users_book_error(self):
        """Test trying to delete another users book gives error."""
        new_user = create_user(email="user2@example.com", password="test123")
        book = create_book(user=new_user)

        url = detail_url(book.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(Book.objects.filter(id=book.id).exists())
