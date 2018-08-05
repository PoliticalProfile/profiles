from django.urls import path

from political_profile.core import views

urlpatterns = [
    path('', views.index)
]