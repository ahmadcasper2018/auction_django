# Generated by Django 4.1.3 on 2022-11-18 13:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("location", "0002_city_title_ar_city_title_en_governorate_title_ar_and_more"),
        ("store", "0005_media"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShippingCompany",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("cost", models.DecimalField(decimal_places=3, max_digits=6)),
                ("phone", models.CharField(max_length=32)),
                (
                    "address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shipping_companys",
                        to="location.address",
                    ),
                ),
            ],
        )
    ]
