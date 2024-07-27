from django.shortcuts import render
from myooo.models import Stock  

from django.http import HttpResponse
import requests
import pandas as pd

# 主頁
def home(request):
    stock = Stock.objects.all()
    stockid = Stock._meta.get_field('stockid').column
    PL = Stock._meta.get_field('PL').column
    return render(request, 'home.html', locals())

#search
def k(url, stock_number, year, season):
    form_data = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'co_id': stock_number,
        'year': year,
        'season': season,
    }
    r = requests.post(url, form_data)
    html_df = pd.read_html(r.text)[1].fillna("")
    return html_df


def search(request):
    url = 'https://mops.twse.com.tw/mops/web/ajax_t164sb04'
    stock_number = ""
    year = ""
    season = ""
    df = None

    if request.method == "POST":
        stock_number = request.POST.get('stock_number')
        year = request.POST.get('year')
        season = request.POST.get('season')
        df = k(url, stock_number, year, season)
        
    return render(request, 'search.html', {
        'stock_number': stock_number,
        'year': year,
        'season': season,
        'df': df
    })



#stock
def g(url, stock_number):
    form_data = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'co_id': stock_number,
        'TYPEK': 'all',
        'isnew': 'true'
    }
    r = requests.post(url, data=form_data)
    html_df = pd.read_html(r.text)[1].fillna("")
    return html_df

def stock(request):
    url = 'https://mops.twse.com.tw/mops/web/ajax_t164sb04'
    stock_number = ""
    df = None

    if request.method == "POST":
        stock_number = request.POST.get('stock_number')
        df = g(url, stock_number)
        
    return render(request, 'stock.html', {
        'stock_number': stock_number,
        'df': df
    })


#reports
import os
import pandas as pd
import requests
from io import StringIO
import time
from django.shortcuts import render
from .models import Stock

def fetch_reports(stock_code):
    urls = [
        'https://mops.twse.com.tw/mops/web/ajax_t164sb03',
        'https://mops.twse.com.tw/mops/web/ajax_t164sb04',
        'https://mops.twse.com.tw/mops/web/ajax_t164sb05'
    ]
    results = []
    for url in urls:
        form_data = {
            'encodeURIComponent': 1,
            'step': 1,
            'firstin': 1,
            'off': 1,
            'co_id': stock_code,
            'TYPEK': 'all',
            'isnew': 'true'
        }
        try:
            r = requests.post(url, data=form_data)
            r.raise_for_status()  # 若響應碼為4xx或5xx，將引發HTTPError
            html_io = StringIO(r.text)
            tables = pd.read_html(html_io)
            if len(tables) > 1:
                df = tables[1]

                results.append(df)
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching reports for stock code {stock_code}: {e}")
            continue  # 繼續到下一個 URL 或股票代碼

    return results

def read_txt_and_update_db(stock_code, reports):
    if len(reports) >= 3:
        try:
            stock = Stock.objects.get(stock_code=stock_code)
        except Stock.DoesNotExist:
            stock = Stock(stock_code=stock_code)

        stock.B = reports[0].to_csv(index=False, sep='\t')
        stock.P = reports[1].to_csv(index=False, sep='\t')
        stock.C = reports[2].to_csv(index=False, sep='\t')
        stock.save()

def validate_and_save_reports_from_csv(csv_file_path, batch_size=10):
    df = pd.read_csv(csv_file_path)
    stock_codes = df['code'].tolist()

    for i in range(0, len(stock_codes), batch_size):
        batch = stock_codes[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1} with stock codes: {batch}")
        
        for stock_code in batch:
            print(f"Processing stock code: {stock_code}")
            attempts = 0
            max_attempts = 3
            reports = None

            while attempts < max_attempts:
                reports = fetch_reports(stock_code)
                if reports:
                    read_txt_and_update_db(stock_code, reports)
                    print(f"Reports for {stock_code} saved and updated successfully.")
                    break
                else:
                    attempts += 1
                    print(f"Attempt {attempts} failed. Retrying...")
                    time.sleep(5)

            if not reports:
                print(f"Failed to fetch reports for {stock_code} after {max_attempts} attempts. Skipping to next stock code.")

def query_report(request):
    if request.method == 'POST':
        stock_code = request.POST.get('stock_code')
        if stock_code:
            try:
                stock = Stock.objects.get(stock_code=stock_code)
                
                # 轉換報告內容為 DataFrame
                df_B = pd.read_csv(StringIO(stock.B), sep='\t')
                df_P = pd.read_csv(StringIO(stock.P), sep='\t')
                df_C = pd.read_csv(StringIO(stock.C), sep='\t')
                
                # 刪除最後兩個欄位
                df_B = df_B.iloc[:, :-2]
                df_P = df_P.iloc[:, :-1]
                df_C = df_C.iloc[:, :-4]
                
                # 將 NaN 值替換為空白字符串
                df_B = df_B.fillna('')
                df_P = df_P.fillna('')
                df_C = df_C.fillna('')
                
                # 生成 HTML 表格
                reports = [
                    {'report_type': '資產負債表', 'content': df_B.to_html(index=False)},
                    {'report_type': '綜合損益表', 'content': df_P.to_html(index=False)},
                    {'report_type': '現金流量表', 'content': df_C.to_html(index=False)},
                ]
                
                return render(request, 'display_reports.html', {'reports': reports})
            except Stock.DoesNotExist:
                return render(request, 'query_report.html', {'error': '股票代碼不存在。'})
    return render(request, 'query_report.html')

def update_reports(request):
    csv_file_path = os.path.join(os.path.dirname(__file__), 'csv', 'stock.csv')
    validate_and_save_reports_from_csv(csv_file_path, batch_size=10)  # 調整批次大小
    return render(request, 'update_reports.html', {'message': 'Reports updated successfully!'})
