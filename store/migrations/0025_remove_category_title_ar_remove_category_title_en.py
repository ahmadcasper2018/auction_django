# Generated by Django 4.1.3 on 2022-11-28 10:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0024_alter_category_title_alter_category_title_ar_and_more")
    ]

    operations = [
        migrations.RemoveField(model_name="category", name="title_ar"),
        migrations.RemoveField(model_name="category", name="title_en"),
    ]
