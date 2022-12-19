# Generated by Django 4.1.4 on 2022-12-19 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("store", "0071_remove_slider_slider_type_page_page_type")]

    operations = [
        migrations.CreateModel(
            name="ProductViewers",
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
                ("viewers", models.PositiveIntegerField(default=0)),
                (
                    "product",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="store.product"
                    ),
                ),
            ],
        )
    ]