from django.shortcuts import render
from myapp.models import Company

#主頁
def company(request):
    company = Company.objects.all()
    stockid = Company._meta.get_field('stockid').column
    abbreviation = Company._meta.get_field('abbreviation').column
    url = Company._meta.get_field('url').column
    industryname = Company._meta.get_field('industryname').column
    return render(request,'company.html',locals())

#新增資料
def insert(request):
    return render(request,'insert.html')

def do_insert(request):
    stockid = request.POST['stockid']
    abbreviation = request.POST['abbreviation']
    url = request.POST['url']
    industryname = request.POST['industryname']

    Company.objects.create(
            stockid=stockid,
            abbreviation=abbreviation,
            url=url,
            industryname=industryname
        )
    return render(request, 'go_company.html')

#詳細資料
def detail(request, stockid):
    detail = Company.objects.get(stockid=stockid)
    return render(request,'detail.html',{'detail':detail})

#更新資料
def update(request, stockid):
    detail = Company.objects.get(stockid=stockid)
    return render(request, 'update.html', {'update': detail})

def do_update(request):
    stockid = request.POST['stockid']
    abbreviation = request.POST['abbreviation']
    url = request.POST['url']
    industryname = request.POST['industryname']

    do_update = Company.objects.get(stockid=stockid)
    do_update.abbreviation = abbreviation
    do_update.url = url
    do_update.industryname = industryname
    do_update.save()

    return render(request, 'go_company.html')
    
#刪除資料
def delete(request, stockid):
    detail = Company.objects.get(stockid=stockid)
    return render(request, 'delete.html', {'delete': detail})

def do_delete(request):
    stockid = request.POST['stockid']
    do_delete = Company.objects.get(stockid=stockid)
    do_delete.delete()
    return render(request, 'go_company.html')










    