# Generated by Django 4.1.4 on 2022-12-19 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("general", "0008_delete_page")]

    operations = [migrations.RemoveField(model_name="contactsettings", name="about")]
