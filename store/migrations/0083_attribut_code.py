# Generated by Django 4.1.4 on 2022-12-24 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("store", "0082_rename_mozaeda_orderlog_auctions")]

    operations = [
        migrations.AddField(
            model_name="attribut",
            name="code",
            field=models.CharField(
                choices=[("color", "Color"), ("size", "size")], max_length=20, null=True
            ),
        )
    ]
