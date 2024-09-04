from django.shortcuts import render



def fund(request):
    return render(request, 'p1_1.html')

def bonds(request):
    return render(request, 'p1_2.html')

def stock(request):
    return render(request, 'p1_3.html')

def etf(request):
    return render(request, 'p1_4.html')

def Report(request):
    return render(request, 'p1_5.html')
