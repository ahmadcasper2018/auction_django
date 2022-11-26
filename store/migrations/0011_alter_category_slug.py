# Generated by Django 4.1.3 on 2022-11-19 00:07

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("store", "0010_product_slug")]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="slug",
            field=autoslug.fields.AutoSlugField(
                editable=False, populate_from="title", unique=True
            ),
        )
    ]