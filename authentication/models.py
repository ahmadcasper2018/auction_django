from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings


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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="phones"
    )
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    type = models.CharField(max_length=64)

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
