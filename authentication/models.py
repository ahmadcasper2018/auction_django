from random import choices

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from store.models import Product


# Create your models here.


class CustomUserManager(UserManager):
    def active(self):
        return self.exclude(is_active=False)


class User(AbstractUser):
    """
    **User Model**
        Default model for User that replaces auth.User.
        Email and username are required.

        **list fields:**

        * username - CharField
        * first_name - CharField
        * last_name - CharField
        * email - EmailField
        * is_staff - BooleanField
        * is_active -BooleanField
        * date_joined - DateTimeField
        * password - CharField
        * last_login - DateTimeField
        * is_active - BooleanField
    """
    MALE = 'M'
    FEMALE = 'F'

    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=False,
        null=False,
    )
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='images/profile/%Y/%m/%d', blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    @property
    def role(self):
        if self.is_superuser:
            return 'superuser'
        elif self.is_staff:
            return 'staff'
        return 'normal'

    def __str__(self):
        return self.email


class Phone(models.Model):
    WHATSAPP = 'whatsapp'
    MOBILE = 'mobile'
    FAX = 'fax'
    WORK = 'work'

    PHONE_TYPES = (
        (WHATSAPP, 'WHATSAPP'),
        (MOBILE, 'MOBILE'),
        (FAX, 'FAX'),
        (WORK, 'WORK')

    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="phones"
    )
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    type = models.CharField(max_length=16, choices=PHONE_TYPES)

    def __str__(self):
        return f'+{self.phone.country_code} {self.phone.national_number}'


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet',
    )
    amount = models.DecimalField(max_digits=8, decimal_places=3)

    def __str__(self):
        return self.pk


class Review(models.Model):
    message = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
    )

    def __str__(self):
        return self.message
