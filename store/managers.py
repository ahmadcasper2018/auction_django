from django.db import models


class CategoryManager(models.Manager):
    def active(self):
        return super().get_queryset().filter(active=True)
