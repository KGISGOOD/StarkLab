# myapp/models.py
from django.db import models

class News(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(max_length=500)
    content = models.TextField()
    source = models.CharField(max_length=100)
    date = models.CharField(max_length=100)

    class Meta:
        db_table = "news"

# Create your models here.
class Music(models.Model):
    song = models.TextField()
    singer = models.TextField()
    last_modify_date = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "music"
