# Generated by Django 4.1.3 on 2022-12-10 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("store", "0045_slidermedia_slider")]

    operations = [
        migrations.AddField(
            model_name="slider",
            name="title_ar",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="slider",
            name="title_en",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="slidermedia",
            name="description_ar",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="slidermedia",
            name="description_en",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="slidermedia",
            name="title_ar",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="slidermedia",
            name="title_en",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="slider",
            name="media",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="sliders",
                to="store.slidermedia",
            ),
        ),
    ]
