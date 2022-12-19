# Generated by Django 4.1.4 on 2022-12-19 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("store", "0079_page_image")]

    operations = [
        migrations.AlterField(
            model_name="page",
            name="page_type",
            field=models.CharField(
                choices=[
                    ("auctions", "Auction"),
                    ("shops", "Shop"),
                    ("bazaar", "Bazar"),
                    ("home", "Home"),
                ],
                default="shops",
                max_length=10,
            ),
        )
    ]
