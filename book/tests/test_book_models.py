"""
Test for book models.
"""
import os
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from book import models
from book.models import book_image_file_path


def create_user(email="user@example.com", password="testpass123"):
    """Create a user for the tests"""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_book(self):
        """Test create book"""
        user = create_user(
            email="user@example.com",
            password="userpass123"
        )

        book = models.Book.objects.create(
            user=user,
            title="Book title",
            price=Decimal("19.99"),
            link="example_link.com",
            description="Book description"
        )

        self.assertEqual(str(book), book.title)

    @patch("book.models.uuid.uuid4")
    def test_book_image_file_path(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = book_image_file_path(None, "example.jpg")

        expected_path = os.path.join("uploads", "book", f"{uuid}.jpg")
        self.assertEqual(file_path, expected_path)
