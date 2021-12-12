from django.conf.urls import url, include
from rest_framework import routers
from . import api_views

#from .serializers import SiteSerializer, ListPageSerializer, ArticleSerializer, ArticleImageSerializer, ArticleItemSerializer


router = routers.DefaultRouter()
router.register(r'users', api_views.UserViewSet)
router.register(r'groups', api_views.GroupViewSet)
router.register(r'sites', api_views.SiteViewSet)
router.register(r'listpages', api_views.ListPageViewSet)
#router.register(r'articles', api_views.ArticleViewSet)
router.register(r'articleimages', api_views.ArticleImageViewSet)
router.register(r'articleitems', api_views.ArticleItemViewSet)

# Привязываем наше API используя автоматическую маршрутизацию.
# Также мы подключим возможность авторизоваться в браузерной версии API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^articles/', api_views.ArticlesList.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]