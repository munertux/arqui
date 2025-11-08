from django.urls import path
from . import views

app_name = 'educational'

urlpatterns = [
    path('', views.EducationalHomeView.as_view(), name='home'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('resource/<slug:slug>/', views.ResourceDetailView.as_view(), name='resource_detail'),
]
