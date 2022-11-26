from decimal import Decimal
from random import choices
from unicodedata import category

from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
from django.urls import reverse

from django_softdelete.models import SoftDeleteModel
from autoslug import AutoSlugField
from django_extensions.db.models import TimeStampedModel

from .managers import CategoryManager
from location.models import Address


# Create your models here.


class Attribut(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title


class AttributDetails(models.Model):
    value = models.CharField(max_length=128)
    attribut = models.ForeignKey(
        Attribut,
        related_name='values',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.value


class Category(SoftDeleteModel):
    BAZAR = 'bazar'
    DIRECT = 'direct'
    MOZAEDA = 'mozaeda'

    CATEGORY_CHOICES = (
        (BAZAR, 'Bazar'),
        (DIRECT, 'Direct'),
        (MOZAEDA, 'Mozaeda'),
    )

    title = models.CharField(max_length=128)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='childs', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='images/category/%Y/%m/%d', blank=True, null=True)
    objects = CategoryManager()

    @property
    def parent_title(self):
        return self.title if self.parent else self.parent.title

    def save(self, *args, **kwargs):
        if (not self.active) and self.products:
            self.products.update(
                is_active=False
            )
        super(Category, self).save(*args, **kwargs)

    @property
    def status(self):
        return 'active' if self.active else 'disabled'

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title


class Product(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='products',
        on_delete=models.CASCADE,

    )

    category = models.ForeignKey(
        Category,
        related_name='products',
        on_delete=models.SET_NULL,
        null=True,

    )
    title = models.CharField(max_length=192)
    description = models.TextField()
    image = models.ImageField(upload_to='images/products/%Y/%m/%d', blank=True, null=True)
    price = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))])
    min_price = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))])
    current_price = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))])
    increase_amount = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))])
    active = models.BooleanField(default=True)
    amount = models.PositiveIntegerField()
    start_time = models.DateTimeField(null=True, blank=False)
    end_time = models.DateTimeField(null=True, blank=False)

    def __str__(self):
        return self.title


class ProductAttribut(models.Model):
    value = models.CharField(max_length=128)
    product = models.ForeignKey(
        Product,
        related_name='attrs',
        on_delete=models.CASCADE,
    )

    attribut = models.ForeignKey(
        Attribut,
        related_name='product_attrs',
        on_delete=models.CASCADE,
    )


class Media(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='media',
        on_delete=models.CASCADE,
    )
    type = models.CharField(max_length=64)
    file = models.FileField(upload_to='images/products_media/%Y/%m/%d')


class ShippingCompany(models.Model):
    name = models.CharField(max_length=255)
    address = models.ForeignKey(
        Address,
        related_name='shipping_companys',
        on_delete=models.CASCADE
    )
    cost = models.DecimalField(max_digits=6, decimal_places=3)
    phone = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Order(models.Model):
    PENDING = 'p'
    SHIPPING = 's'
    CANCLED = 'c'
    DONE = 'd'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (SHIPPING, 'Shipping'),
        (CANCLED, 'Cancled'),
        (DONE, 'Done')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True

    )
    shipping_company = models.ForeignKey(
        ShippingCompany,
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True
    )
    address = models.ForeignKey(
        Address,
        related_name='orders',
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f'order by {self.user} shipped with {self.shipping_company}'


class ProductOrder(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='product_orders',
        on_delete=models.SET_NULL,
        null=True,

    )

    order = models.ForeignKey(
        Order,
        related_name='product_orders',
        on_delete=models.SET_NULL,
        null=True,

    )
    quantity = models.PositiveIntegerField(null=True)
    attribut = models.JSONField(null=True, blank=True)

    @property
    def price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'User {self.order.user} ordered {self.quantity} of {self.product.title}'


class CategoryAttribute(models.Model):
    category = models.ForeignKey(
        Category,
        related_name='category_attrs',
        on_delete=models.SET_NULL,
        null=True,

    )
    attribut = models.ForeignKey(
        Attribut,
        related_name='category_attrs',
        on_delete=models.SET_NULL,
        null=True,

    )


class OrderLog(TimeStampedModel):
    by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="bazar_logs",
        null=True,
        blank=True,
    )
    order = models.ForeignKey(
        ProductOrder,
        on_delete=models.SET_NULL,
        related_name="logs",
        null=True,
        blank=True,
    )

    mozaeda = models.BooleanField(default=False)

    def __str__(self):
        return f"log by {self.by} on {self.product}"
