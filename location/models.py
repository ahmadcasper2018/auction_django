from django.db import models
from django.conf import settings


# Create your models here.

class Governorate(models.Model):
    code = models.CharField(max_length=255)
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title}:{self.code}"


class City(models.Model):
    title = models.CharField(max_length=255)
    governorate = models.ForeignKey(
        Governorate,
        related_name="cities",
        on_delete=models.CASCADE,

    )

    def __str__(self):
        return self.title


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='addresses',
                             null=True)
    address = models.CharField(max_length=255)
    city = models.ForeignKey(
        City,
        related_name="addresses",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.address
