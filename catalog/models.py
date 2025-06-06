"""
Catalog database models.
"""
from django.db import models


class Genre(models.Model):
    """Genre object"""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Author(models.Model):
    """Author object"""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
