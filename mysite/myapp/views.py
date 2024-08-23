from django.shortcuts import render

def index(request):
    return render(request, 'myapp/index.html')

def about(request):
    return render(request, 'myapp/about.html')

def contact(request):
    return render(request, 'myapp/contact.html')

def gallery(request):
    return render(request, 'myapp/gallery.html')

def products(request):
    return render(request, 'myapp/products.html')

def project1(request):
    return render(request, 'myapp/project1.html')

def project2(request):
    return render(request, 'myapp/project2.html')

def project3(request):
    return render(request, 'myapp/project3.html')

def project4(request):
    return render(request, 'myapp/project4.html')

def project5(request):
    return render(request, 'myapp/project5.html')

def project6(request):
    return render(request, 'myapp/project6.html')