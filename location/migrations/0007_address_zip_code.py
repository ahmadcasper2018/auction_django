# Generated by Django 4.1.3 on 2022-12-09 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("location", "0006_alter_address_user")]

    operations = [
        migrations.AddField(
            model_name="address",
            name="zip_code",
            field=models.CharField(max_length=255, null=True),
        )
    ]
