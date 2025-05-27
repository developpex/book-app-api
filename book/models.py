"""
Book database models.
"""
import os
import uuid

from django.conf import settings
from django.db import models


def book_image_file_path(instance, filename):
    """Generate file path for new book image"""
    ext = os.path.splitext(filename)[1]  # keeps original file extension
    filename = f"{uuid.uuid4()}{ext}"

    return os.path.join("uploads", "book", filename)


class Book(models.Model):
    """Book object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255)
    genres = models.ManyToManyField("catalog.Genre")
    authors = models.ManyToManyField("catalog.Author")
    image = models.ImageField(null=True, upload_to=book_image_file_path)

    def __str__(self):
        return self.title
