# Generated by Django 4.1.4 on 2023-01-13 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("store", "0091_remove_auctionorder_order_product")]

    operations = [
        migrations.AddField(
            model_name="auctionorder",
            name="address",
            field=models.CharField(max_length=128, null=True),
        )
    ]