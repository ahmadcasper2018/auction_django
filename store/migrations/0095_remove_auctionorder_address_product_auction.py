# Generated by Django 4.1.4 on 2023-01-13 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("store", "0094_auctionorder_user_auctionlog")]

    operations = [
        migrations.RemoveField(model_name="auctionorder", name="address"),
        migrations.AddField(
            model_name="product",
            name="auction",
            field=models.BooleanField(default=False),
        ),
    ]
