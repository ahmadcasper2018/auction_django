# Generated by Django 4.1.4 on 2022-12-14 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("store", "0055_auctionorder")]

    operations = [
        migrations.AlterField(
            model_name="auctionorder",
            name="current_payment",
            field=models.DecimalField(decimal_places=3, default=0, max_digits=10),
        )
    ]