from django.shortcuts import render

def voice_search(request):
    return render(request, 'voice_search.html')

