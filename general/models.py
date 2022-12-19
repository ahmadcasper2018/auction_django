from django.db import models

# Create your models here.
from store.models import Slider


class ContactSettings(models.Model):
    phone = models.CharField(max_length=64, null=True, blank=True)
    instagram = models.CharField(max_length=64, null=True, blank=True)
    whatsapp = models.CharField(max_length=64, null=True, blank=True)
    facebook = models.CharField(max_length=64, null=True, blank=True)
    fax = models.CharField(max_length=64, null=True, blank=True)
    youtube = models.CharField(max_length=64, null=True, blank=True)
    gmail = models.CharField(max_length=64, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    lang = models.CharField(max_length=64, null=True, blank=True)
    lat = models.CharField(max_length=64, null=True, blank=True)


class KeyWord(models.Model):
    keyword = models.CharField(max_length=128)

    def __str__(self):
        return self.keyword


class Question(models.Model):
    question = models.CharField(max_length=512)
    answer = models.TextField()
    keyword = models.ManyToManyField(
        KeyWord,
        related_name="question_kewords"
    )

    def __str__(self):
        return self.question
