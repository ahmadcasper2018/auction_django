# Generated by Django 4.1.4 on 2022-12-18 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("store", "0061_attributvalue")]

    operations = [
        migrations.RemoveField(model_name="productattribut", name="value_ar"),
        migrations.RemoveField(model_name="productattribut", name="value_en"),
    ]
