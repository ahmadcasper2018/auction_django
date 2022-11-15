from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


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
    avatar = models.ImageField(upload_to='images/', blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()
