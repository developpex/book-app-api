"""
Test for book models.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from book import models


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
