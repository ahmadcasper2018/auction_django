# Generated by Django 3.2 on 2022-11-24 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_productorder_request_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='productorder',
            name='request_type',
        ),
        migrations.AddField(
            model_name='product',
            name='end_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='start_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='productorder',
            name='quantity',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='category',
            name='slug',
        ),
    ]
