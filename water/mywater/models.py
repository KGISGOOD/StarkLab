from django.db import models

class News(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(max_length=500)
    content = models.TextField()
    source = models.CharField(max_length=100)
    date = models.CharField(max_length=100)

    class Meta:
        db_table = "news"

