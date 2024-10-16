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
    cash_and_cash_equivalents = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='現金及約當現金')
    total_liabilities = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='負債總額')
    total_assets = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='資產總額')
    net_accounts_receivable = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='應收帳款淨額')
    total_equity = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='權益總額')
    non_current_assets = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='非流動資產合計')
    non_current_liabilities = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='非流動負債合計')
    current_assets = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='流動資產合計')
    current_liabilities = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='流動負債合計')
    inventory = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='存貨')
    total_operating_income = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='營業收入合計')
    gross_margin = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='毛利率')
    operating_margin = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='營業利益率')
    net_margin = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='淨利率')
    net_profit_loss = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='本期淨利（淨損）')
    eps = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='基本每股盈餘 (EPS)')
    cash_dividends = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='發放現金股利')
    operating_safety_margin = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='經營安全邊際')
    roe = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='股東權益報酬率 (ROE)')
    financial_leverage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='財務槓桿')
    cash_to_assets_ratio = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='現金及約當現金/資產總額比率')
    accounts_receivable_days = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='應收帳款收現日')
    cash_flow_ratio = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='現金流量比率')
    cash_adequacy_ratio = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='現金允當比率')
    cash_reinvestment_ratio = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='現金再投資比率')
    class Meta:
        db_table = "stockMetrics"