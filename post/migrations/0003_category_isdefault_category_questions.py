# Generated by Django 4.1.2 on 2022-11-03 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("post", "0002_category_remove_post_body_post_answers_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="isDefault",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="category", name="questions", field=models.JSONField(null=True),
        ),
    ]
