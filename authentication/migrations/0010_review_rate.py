# Generated by Django 4.1.4 on 2022-12-24 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("authentication", "0009_walletlog")]

    operations = [
        migrations.AddField(
            model_name="review",
            name="rate",
            field=models.PositiveIntegerField(default=1),
        )
    ]
