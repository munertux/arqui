from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
path('', views.BlogPostListView.as_view(), name='home'),
path('nueva/', views.BlogPostCreateView.as_view(), name='create'),
path('reportes/', views.BlogReportListView.as_view(), name='report_list'),
path('<slug:slug>/reaccionar/', views.BlogPostToggleReactionView.as_view(), name='toggle_reaction'),
path('<slug:slug>/reportar/', views.BlogPostReportView.as_view(), name='report'),
path('<slug:slug>/', views.BlogPostDetailView.as_view(), name='detail'),
]
