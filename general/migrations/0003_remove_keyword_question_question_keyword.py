# Generated by Django 4.1.3 on 2022-11-26 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "general",
            "0002_contactsettings_about_alter_contactsettings_facebook_and_more",
        )
    ]

    operations = [
        migrations.RemoveField(model_name="keyword", name="question"),
        migrations.AddField(
            model_name="question",
            name="keyword",
            field=models.ManyToManyField(
                related_name="question_kewords", to="general.keyword"
            ),
        ),
    ]
