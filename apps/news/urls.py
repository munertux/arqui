from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.NewsHomeView.as_view(), name='home'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('create/', views.CreatePostView.as_view(), name='create_post'),
]
