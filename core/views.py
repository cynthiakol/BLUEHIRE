from django.shortcuts import render

# homepage
def homepage(request):
    return render(request, 'core/home.html')

# employers landing page
def employer(request):
    return render(request, 'core/employer.html')

# new sign-in / register page
def signin_register(request):
    return render(request, 'core/signin_register.html')

def contact(request):
    return render(request, 'core/contact.html')

def terms(request):
    return render(request, 'core/terms.html')

def privacy(request):
    return render(request, 'core/privacy.html')

def help_center(request):
    return render(request, 'core/help_center.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def facebook_data_deletion(request):
    return JsonResponse({
        'url': 'https://apogamic-optionally-ciera.ngrok-free.dev/accounts/data-deletion/',
        'confirmation_code': 'bluehire-deletion-request'
    })