from django.shortcuts import render


def home(request):
    # By default, shows a Superuser home page.
    # (might need home pages for Students later)
    return render(request, 'home/home.html')