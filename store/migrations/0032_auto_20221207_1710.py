# Generated by Django 3.2.1 on 2022-12-07 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0031_alter_orderlog_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='productattribut',
            name='value_ar',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='productattribut',
            name='value_en',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
