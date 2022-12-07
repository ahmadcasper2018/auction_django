# Generated by Django 3.2.1 on 2022-12-07 20:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0006_alter_address_user'),
        ('store', '0032_auto_20221207_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='address',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product', to='location.address'),
        ),
    ]
