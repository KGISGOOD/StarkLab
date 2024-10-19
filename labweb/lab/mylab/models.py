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
    image = models.URLField(max_length=500, blank=True, null=True)  # 新增圖片欄位
    link = models.URLField(max_length=500)
    content = models.TextField()
    source = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    class Meta:
        db_table = "news"
        

class StockMetrics(models.Model):
    stock_code = models.CharField(max_length=10, unique=True, verbose_name='股票代號')  # 股票代號
    毛利率 = models.FloatField(null=True, blank=True, verbose_name='毛利率')
    營業利益率 = models.FloatField(null=True, blank=True, verbose_name='營業利益率')
    淨利率 = models.FloatField(null=True, blank=True, verbose_name='淨利率')
    EPS = models.FloatField(null=True, blank=True, verbose_name='基本每股盈餘 (EPS)')
    經營安全邊際 = models.FloatField(null=True, blank=True, verbose_name='經營安全邊際')
    ROE = models.FloatField(null=True, blank=True, verbose_name='股東權益報酬率 (ROE)')

    財務槓桿 = models.FloatField(null=True, blank=True, verbose_name='財務槓桿')
    應收帳款收現日 = models.FloatField(null=True, blank=True, verbose_name='應收帳款收現日')
    銷貨天數 = models.FloatField(null=True, blank=True, verbose_name='銷貨天數')
    加分項 = models.FloatField(null=True, blank=True, verbose_name='加分項')

    class Meta:
        db_table = "stockMetrics"


