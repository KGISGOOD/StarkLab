from django.shortcuts import render, redirect
from .forms import PersonForm
from .models import Person

def index(request):
    return render(request, 'index.html')

def achievements(request):
    return render(request, 'achievements.html')

def team(request):
    return render(request, 'team.html')

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
