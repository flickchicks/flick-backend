# Generated by Django 3.0.7 on 2020-08-07 03:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0003_remove_profile_ratings"),
        ("comment", "0004_auto_20200803_0545"),
        ("like", "0002_auto_20200806_0043"),
    ]

    operations = [
        migrations.RenameField(model_name="like", old_name="comment_id", new_name="comment",),
        migrations.AlterUniqueTogether(name="like", unique_together={("liker", "comment")},),
    ]