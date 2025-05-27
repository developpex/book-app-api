"""
Test for catalog models.
"""

from django.test import TestCase

from catalog import models


class ModelTest(TestCase):
    """Test models."""

    def test_crate_genre(self):
        """Test create genre"""

        genre = models.Genre.objects.create(
            name="Genre"
        )

        self.assertEqual(str(genre), genre.name)

    def test_crate_author(self):
        """Test create author"""

        author = models.Author.objects.create(
            name="Author"
        )

        self.assertEqual(str(author), author.name)
