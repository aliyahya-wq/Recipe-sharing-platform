from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def recipes(request):
    return render(request, 'recipes.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')