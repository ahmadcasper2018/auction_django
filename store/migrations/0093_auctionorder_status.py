# Generated by Django 4.1.4 on 2023-01-13 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("store", "0092_auctionorder_address")]

    operations = [
        migrations.AddField(
            model_name="auctionorder",
            name="status",
            field=models.CharField(
                choices=[
                    ("approved", "approved"),
                    ("pending", "pending"),
                    ("expired", "expired"),
                ],
                max_length=20,
                null=True,
            ),
        )
    ]
