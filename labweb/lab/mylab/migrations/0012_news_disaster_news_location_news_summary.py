# Generated by Django 5.1.3 on 2024-12-04 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mylab", "0011_news_region"),
    ]

    operations = [
        migrations.AddField(
            model_name="news",
            name="disaster",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="news",
            name="location",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="news",
            name="summary",
            field=models.TextField(blank=True, null=True),
        ),
    ]