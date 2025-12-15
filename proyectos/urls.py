from django.urls import path
from . import views

urlpatterns = [
    path('registrar/<int:evento_id>/', views.registrar_proyecto, name='registrar_proyecto'),
]
