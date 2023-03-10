# Generated by Django 4.1.3 on 2022-12-10 11:11

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("store", "0039_auto_20221209_1228")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="decrease_amount",
            field=models.DecimalField(
                decimal_places=3,
                max_digits=10,
                null=True,
                validators=[django.core.validators.MinValueValidator(Decimal("0.001"))],
            ),
        ),
        migrations.AddField(
            model_name="product", name="new", field=models.BooleanField(default=False)
        ),
        migrations.AddField(
            model_name="product", name="used", field=models.BooleanField(default=False)
        ),
        migrations.AlterField(
            model_name="product",
            name="current_price",
            field=models.DecimalField(decimal_places=3, max_digits=10),
        ),
        migrations.AlterField(
            model_name="product",
            name="increase_amount",
            field=models.DecimalField(
                decimal_places=3,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal("0.001"))],
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="min_price",
            field=models.DecimalField(
                decimal_places=3,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal("0.001"))],
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(
                decimal_places=3,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal("0.001"))],
            ),
        ),
    ]
