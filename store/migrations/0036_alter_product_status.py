# Generated by Django 3.2.1 on 2022-12-07 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0035_product_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('p', 'Pending'), ('a', 'Accepted'), ('r', 'Rejected')], default='p', max_length=1),
        ),
    ]
