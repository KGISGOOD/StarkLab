from django.shortcuts import render, redirect
from .forms import PersonForm
from .models import Person

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def gallery(request):
    return render(request, 'gallery.html')

def products(request):
    return render(request, 'products.html')

def project1(request):
    return render(request, 'project1.html')

def project2(request):
    return render(request, 'project2.html')

def project3(request):
    return render(request, 'project3.html')

def project4(request):
    return render(request, 'project4.html')

def project5(request):
    return render(request, 'project5.html')

def project6(request):
    return render(request, 'project6.html')

def add_person(request):
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('person_list')
    else:
        form = PersonForm()
    return render(request, 'myapp/add_person.html', {'form': form})

def person_list(request):
    persons = Person.objects.all()
    return render(request, 'myapp/person_list.html', {'persons': persons})
