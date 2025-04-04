# Generated by Django 5.1.3 on 2024-12-21 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mylab", "0014_rename_event_news_title_remove_news_daily_records_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="news",
            old_name="title",
            new_name="event",
        ),
        migrations.AddField(
            model_name="news",
            name="daily_records",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="news",
            name="disaster",
            field=models.CharField(
                choices=[
                    ("乾旱", "乾旱"),
                    ("旱災", "旱災"),
                    ("豪雨", "豪雨"),
                    ("大雨", "大雨"),
                    ("水災", "水災"),
                    ("洪水", "洪水"),
                    ("颱風", "颱風"),
                    ("颶風", "颶風"),
                    ("氣旋", "氣旋"),
                    ("暴雨", "暴雨"),
                    ("淹水", "淹水"),
                    ("地震", "地震"),
                    ("海嘯", "海嘯"),
                    ("火山爆發", "火山爆發"),
                    ("土石流", "土石流"),
                    ("山體滑坡", "山體滑坡"),
                    ("未知", "未知"),
                ],
                default="未知",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="news",
            name="links",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="news",
            name="location",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="news",
            name="recent_update",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="news",
            name="summary",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="news",
            name="date",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="news",
            name="region",
            field=models.CharField(
                choices=[("國內", "國內"), ("國外", "國外")],
                default="未知",
                max_length=10,
            ),
        ),
    ]
