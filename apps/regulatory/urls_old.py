from django.urls import path
from . import views

app_name = 'regulatory'

urlpatterns = [
    # Página principal del módulo regulatorio
    path('', views.RegulatoryHomeView.as_view(), name='home'),
    
    # Ley 1715 de 2014 (ruta específica)
    path('ley-1715-2014/', views.Ley1715DetailView.as_view(), name='ley_1715'),
    
    # Lista de marcos legales
    path('marco-legal/', views.LegalFrameworkListView.as_view(), name='legal_framework_list'),
    
    # Actualización AJAX de la Ley 1715
    path('api/update-ley-1715/', views.update_ley_1715_view, name='update_ley_1715'),
    
    # URLs existentes
    path('categoria/<slug:category_slug>/', views.CategoryView.as_view(), name='category'),
    path('documento/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('buscar/', views.SearchView.as_view(), name='search'),
].urls import path
from . import views

app_name = 'regulatory'

urlpatterns = [
    path('', views.RegulatoryHomeView.as_view(), name='home'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('document/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('search/', views.SearchView.as_view(), name='search'),
]
