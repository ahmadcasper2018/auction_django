# Generated by Django 3.2.1 on 2023-01-21 16:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0109_alter_order_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='category',
            name='is_deleted',
        ),
    ]