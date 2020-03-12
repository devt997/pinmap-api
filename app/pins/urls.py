from django.urls import path, include
from rest_framework.routers import DefaultRouter

from pins import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)

app_name = 'pins'

urlpatterns = [
    path('', include(router.urls))
]
