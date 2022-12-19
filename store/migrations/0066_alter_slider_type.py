# Generated by Django 4.1.4 on 2022-12-19 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("store", "0065_rename_content_slider_description_and_more")]

    operations = [
        migrations.AlterField(
            model_name="slider",
            name="type",
            field=models.CharField(
                choices=[("auction", "Auction"), ("shop", "Shop"), ("bazar", "Direct")],
                default="shop",
                max_length=10,
            ),
        )
    ]
