# Generated by Django 3.0.6 on 2020-08-21 18:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("notification", "0003_auto_20200816_2230")]

    operations = [migrations.AlterModelOptions(name="notification", options={"ordering": ["-created_at"]})]