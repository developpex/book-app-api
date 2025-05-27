"""
Tests for the catalog api
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from catalog.models import Author
from catalog.serializers import AuthorSerializer

AUTHOR_URL = reverse("catalog:author-list")


def detail_url(author_id):
    """Create and return an author detail url"""
    return reverse("catalog:author-detail", args=[author_id])


def create_author(**params):
    """Create and return an author"""
    defaults = {
        "name": "Author Name"
    }
    defaults.update(params)

    author = Author.objects.create(**defaults)
    return author


class PublicAuthorApiTests(TestCase):
    """Test unauthenticated API request."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(AUTHOR_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAuthorApiTests(TestCase):
    """Test authenticated API request."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@example.com", "userpass123"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_authors(self):
        """Test retrieving a list of authors."""
        create_author(name="Author_one")
        create_author(name="Author_two")

        res = self.client.get(AUTHOR_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        authors = Author.objects.all().order_by("-name")
        serializer = AuthorSerializer(authors, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_update_author(self):
        """Test for updating an author"""
        author = create_author(name="Author_one")
        payload = {
            "name": "Author_two"
        }
        url = detail_url(author.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        author.refresh_from_db()
        self.assertEqual(author.name, payload["name"])

    def test_delete_author(self):
        author = create_author(name="Author_one")

        url = detail_url(author.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Author.objects.filter(id=author.id).exists())
