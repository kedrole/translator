from django.contrib.auth.models import User, Group
from .serializers import UserSerializer, GroupSerializer

from .models import Site, ListPage, Article, ArticleImage, ArticleItem
from .serializers import SiteSerializer, ListPageSerializer, ArticleSerializer, ArticleImageSerializer, ArticleItemSerializer

from rest_framework import viewsets, generics

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class ArticlesList(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer

class ListPageViewSet(viewsets.ModelViewSet):
    queryset = ListPage.objects.all()
    serializer_class = ListPageSerializer

class ArticleImageViewSet(viewsets.ModelViewSet):
    queryset = ArticleImage.objects.all()
    serializer_class = ArticleImageSerializer

class ArticleItemViewSet(viewsets.ModelViewSet):
    queryset = ArticleItem.objects.all()
    serializer_class = ArticleItemSerializer