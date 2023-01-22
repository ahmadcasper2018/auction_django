# Generated by Django 4.1.4 on 2023-01-22 21:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [("store", "0111_alter_order_status")]

    operations = [
        migrations.AddField(
            model_name="order",
            name="createdat",
            field=models.DateField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        )
    ]
