from django.db import models

class News(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(max_length=500)
    content = models.TextField()
    source = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    image = models.URLField(max_length=500, blank=True, null=True)  # 新增圖片欄位


    class Meta:
        db_table = "news"

