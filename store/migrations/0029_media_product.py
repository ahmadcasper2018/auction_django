# Generated by Django 3.2.1 on 2022-12-01 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0028_auto_20221201_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='store.product'),
        ),
    ]
