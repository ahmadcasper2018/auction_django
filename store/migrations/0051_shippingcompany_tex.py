# Generated by Django 4.1.3 on 2022-12-13 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("store", "0050_media_alt_media_attribut_media_value")]

    operations = [
        migrations.AddField(
            model_name="shippingcompany",
            name="tex",
            field=models.DecimalField(decimal_places=3, max_digits=6, null=True),
        )
    ]
