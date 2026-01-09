# urls.py
from django.urls import path
from .views import kbo_best_ba

urlpatterns = [
    path("kbo/", kbo_best_ba),
]
