# Generated by Django 4.1.4 on 2022-12-18 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0063_remove_productattribut_value_productattribut_values")
    ]

    operations = [
        migrations.AlterField(
            model_name="media",
            name="attributes",
            field=models.ManyToManyField(related_name="medias", to="store.attribut"),
        )
    ]