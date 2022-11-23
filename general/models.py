from django.db import models


# Create your models here.
class ContactSettings(models.Model):
    phone = models.CharField(max_length=64, null=True, blank=True)
    instagram = models.CharField(max_length=64, null=True, blank=True)
    whatsapp = models.CharField(max_length=64, null=True, blank=True)
    facebook = models.CharField(max_length=64, null=True, blank=True)
    gmail = models.CharField(max_length=64, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    about = models.TextField(null=True, blank=True)


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
