# Generated by Django 3.2.1 on 2022-12-07 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0003_remove_keyword_question_question_keyword'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactsettings',
            name='lang',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='contactsettings',
            name='lat',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]