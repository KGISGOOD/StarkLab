from django.db import models

class Stock(models.Model):
    stock_code = models.CharField(max_length=10, unique=True)  # 股票代號
    B = models.TextField()  # 報表 1 的 CSV 數據
    P = models.TextField()  # 報表 2 的 CSV 數據
    C = models.TextField()  # 報表 3 的 CSV 數據

    class Meta:
        db_table = "stock"


class News(models.Model):
    event = models.CharField(max_length=255)  # 事件名稱
    image = models.URLField(max_length=500, blank=True, null=True)  # 事件圖片URL
    link = models.URLField(max_length=500)  # 相關新聞連結
    content = models.TextField()  # 新聞內容
    source = models.CharField(max_length=100)  # 新聞來源
    date = models.DateField()  # 事件日期
    recent_update = models.DateField(blank=True, null=True)  # 最新更新日期
    region = models.CharField(
        max_length=10,
        choices=[('國內', '國內'), ('國外', '國外')],
        default='未知'
    )  # 地理範圍
    location = models.CharField(max_length=255, blank=True, null=True)  # 地點
    disaster = models.CharField(
        max_length=50,
        choices=[
            ('乾旱', '乾旱'), ('旱災', '旱災'), ('豪雨', '豪雨'), ('大雨', '大雨'), 
            ('水災', '水災'), ('洪水', '洪水'), ('颱風', '颱風'), ('颶風', '颶風'),
            ('氣旋', '氣旋'), ('暴雨', '暴雨'), ('淹水', '淹水'), ('地震', '地震'),
            ('海嘯', '海嘯'), ('火山爆發', '火山爆發'), ('土石流', '土石流'), 
            ('山體滑坡', '山體滑坡'), ('未知', '未知')
        ],
        default='未知'
    )  # 災害類型
    summary = models.TextField(blank=True, null=True)  # 事件摘要
    daily_records = models.JSONField(blank=True, null=True)  # 每日進展記錄
    links = models.JSONField(blank=True, null=True)  # 新聞連結資料

    class Meta:
        db_table = "news"  # 指定資料表名稱為 "news"


        

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

