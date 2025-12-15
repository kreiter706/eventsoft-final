from django.shortcuts import render
from django.urls import reverse


def dashboard(request):
    """Vista sencilla de dashboard inicial con botones a las rutas principales."""
    context = {
        'eventos_url': reverse('eventos_proximos'),
        'login_url': reverse('login'),
    }
    return render(request, 'dashboard.html', context)
