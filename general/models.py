from django.db import models


# Create your models here.
class ContactSettings(models.Model):
    phone = models.CharField(max_length=64)
    instagram = models.CharField(max_length=64)
    whatsapp = models.CharField(max_length=64)
    facebook = models.CharField(max_length=64)
    gmail = models.CharField(max_length=64)
    location = models.CharField(max_length=255)


class Question(models.Model):
    question = models.CharField(max_length=512)
    answer = models.TextField()

    def __str__(self):
        return self.question


class KeyWord(models.Model):
    keyword = models.CharField(max_length=128)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="keywords"

    )

    def __str__(self):
        return self.keyword
