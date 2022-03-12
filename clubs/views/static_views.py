
"""Static views of the clubs app."""
from clubs.views.helpers import login_prohibited
from django.shortcuts import render


@login_prohibited
def home(request):
    return render(request, 'home.html')
