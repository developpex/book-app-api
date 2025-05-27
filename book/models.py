"""
Book database models.
"""

from django.conf import settings
from django.db import models


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
    genre = models.ManyToManyField("catalog.Genre")

    def __str__(self):
        return self.title
