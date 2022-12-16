import os
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

from django_softdelete.models import SoftDeleteModel
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
    title = models.CharField(max_length=128)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='childs', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='images/category/%Y/%m/%d', blank=True, null=True)
    objects = CategoryManager()

    @property
    def parent_title(self):
        if not self.parent:
            return self.title
        else:
            return self.parent.title

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
    PENDING = 'p'
    ACCEPTED = 'a'
    REJECTED = 'r'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    )
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
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        null=True,
        related_name='product',
    )
    title = models.CharField(max_length=192)
    description = models.TextField()
    image = models.ImageField(upload_to='images/products/%Y/%m/%d', blank=True, null=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))])
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))])
    current_price = models.DecimalField(
        max_digits=10,
        decimal_places=3,
    )
    increase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))])
    active = models.BooleanField(default=True)
    amount = models.PositiveIntegerField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=False)
    end_time = models.DateTimeField(null=True, blank=False)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    reject_message = models.CharField(max_length=512, null=True)
    new = models.BooleanField(default=False)
    used = models.BooleanField(default=False)
    decrease_amount = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        validators=[MinValueValidator(Decimal('0.001'))])
    stock = models.PositiveIntegerField(default=1)
    sale = models.BooleanField(default=False)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def product_type(self):
        p_type = self.category
        while p_type.parent:
            test = p_type.parent
            if not test:
                return p_type.title
            p_type = p_type.parent
        return p_type.title

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
    file = models.FileField(upload_to='images/products_media/%Y/%m/%d')
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        related_name='media',
        null=True
    )
    attributes = models.ManyToManyField(
        Attribut,
        null=True,
        related_name='medias',
    )
    alt = models.CharField(max_length=32, null=True)
    value = models.CharField(max_length=64, null=True)

    @property
    def type(self):
        name, extension = os.path.splitext(self.file.name)
        return extension


class ShippingCompany(models.Model):
    name = models.CharField(max_length=255)
    address = models.ForeignKey(
        Address,
        related_name='shipping_companys',
        on_delete=models.CASCADE
    )
    cost = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    phone = models.CharField(max_length=32)
    tax = models.DecimalField(max_digits=6, decimal_places=3, default=0)

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
        return f"{self.pk}"


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
        Order,
        on_delete=models.SET_NULL,
        related_name="logs",
        null=True,
        blank=True,
    )

    mozaeda = models.BooleanField(default=False)

    def __str__(self):
        return f"log by {self.by} on {self.order}"


class Brand(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='brands',
        null=True,

    )
    image = models.ImageField(upload_to='images/brands/%Y/%m/%d', blank=True, null=True)

    def __str__(self):
        return self.title


class Slider(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()


class SliderMedia(models.Model):
    file = models.FileField(upload_to='images/slider-media/%Y/%m/%d')
    slider = models.ForeignKey(
        Slider,
        on_delete=models.SET_NULL,
        null=True,
        related_name='media'
    )


class AuctionOrder(models.Model):
    auction_product = models.ForeignKey(
        Product,
        related_name='auction_orders',
        on_delete=models.SET_NULL,
        null=True,

    )

    order_product = models.ForeignKey(
        Order,
        related_name='auction_orders',
        on_delete=models.SET_NULL,
        null=True,

    )
    direct = models.BooleanField(default=False)
    current_payment = models.DecimalField(max_digits=10, decimal_places=3, default=0)
