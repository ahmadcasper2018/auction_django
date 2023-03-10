# Generated by Django 4.1.4 on 2022-12-25 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("general", "0009_remove_contactsettings_about")]

    operations = [
        migrations.AddField(
            model_name="keyword",
            name="keyword_ar",
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="keyword",
            name="keyword_en",
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="question", name="answer_ar", field=models.TextField(null=True)
        ),
        migrations.AddField(
            model_name="question", name="answer_en", field=models.TextField(null=True)
        ),
        migrations.AddField(
            model_name="question",
            name="question_ar",
            field=models.CharField(max_length=512, null=True),
        ),
        migrations.AddField(
            model_name="question",
            name="question_en",
            field=models.CharField(max_length=512, null=True),
        ),
    ]
