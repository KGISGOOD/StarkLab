# Generated by Django 5.0.6 on 2024-10-14 17:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mylab", "0004_remove_news_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="news",
            name="image",
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
