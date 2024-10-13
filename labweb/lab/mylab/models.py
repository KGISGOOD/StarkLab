from django.db import models

class Stock(models.Model):
    stock_code = models.CharField(max_length=10, unique=True)  # 股票代號
    B = models.TextField()  # 報表 1 的 CSV 數據
    P = models.TextField()  # 報表 2 的 CSV 數據
    C = models.TextField()  # 報表 3 的 CSV 數據

    class Meta:
        db_table = "stock"

class News(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(max_length=500)
    content = models.TextField()
    source = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    image = models.URLField(max_length=500, blank=True, null=True)  # 新增圖片欄位

    class Meta:
        db_table = "news"

