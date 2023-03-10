# Generated by Django 4.1.3 on 2022-11-19 11:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("store", "0013_categoryattribute")]

    operations = [
        migrations.AlterField(
            model_name="productattribut",
            name="attribut",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product_attrs",
                to="store.attribut",
            ),
        )
    ]
