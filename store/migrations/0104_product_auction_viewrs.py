# Generated by Django 4.1.4 on 2023-01-15 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("store", "0103_remove_product_auction")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="auction_viewrs",
            field=models.PositiveIntegerField(blank=True, null=True),
        )
    ]