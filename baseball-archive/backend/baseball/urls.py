from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlayerViewSet

# Router 설정
router = DefaultRouter()
router.register(r'players', PlayerViewSet, basename='player')

app_name = 'baseball'

urlpatterns = [
    path('', include(router.urls)),
]

