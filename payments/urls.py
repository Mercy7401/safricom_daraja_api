from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("status/<int:pk>/", views.status, name="status"),
    path("status/<int:pk>/json/", views.status_json, name="status_json"),
    path("history/", views.history, name="history"),
    path("callback/", views.callback, name="callback"),
]