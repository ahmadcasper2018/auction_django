# Generated by Django 4.1.4 on 2022-12-16 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("store", "0056_alter_auctionorder_current_payment")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="discount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=2),
        ),
        migrations.AddField(
            model_name="product", name="sale", field=models.BooleanField(default=False)
        ),
    ]
