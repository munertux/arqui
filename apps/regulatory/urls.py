from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'regulatory'

urlpatterns = [
    # Redirigir la raíz del módulo regulatorio al listado (marco-legal)
    path('', RedirectView.as_view(pattern_name='regulatory:legal_framework_list', permanent=False), name='home'),
    
    # Ley 1715 de 2014 (ruta específica)
    # Lista de marcos legales
    path('marco-legal/', views.LegalFrameworkListView.as_view(), name='legal_framework_list'),
    path('marco-legal/<str:document_type>/<str:document_number>/<int:year>/', views.LegalFrameworkDetailView.as_view(), name='legal_framework_detail'),

    # Rutas legadas
    path(
        'ley-1715-2014/',
        RedirectView.as_view(pattern_name='regulatory:legal_framework_detail', permanent=True),
        {'document_type': 'ley', 'document_number': '1715', 'year': 2014}
    ),
    path(
        'ley-2099-2021/',
        RedirectView.as_view(pattern_name='regulatory:legal_framework_detail', permanent=True),
        {'document_type': 'ley', 'document_number': '2099', 'year': 2021}
    ),

    # Gestión administrativa de marcos legales
    path('admin/frameworks/', views.LegalFrameworkAdminListView.as_view(), name='admin_framework_list'),
    path('admin/frameworks/nuevo/', views.LegalFrameworkCreateView.as_view(), name='admin_framework_create'),
    path('admin/frameworks/<int:pk>/editar/', views.LegalFrameworkUpdateView.as_view(), name='admin_framework_update'),
    path('admin/frameworks/<int:pk>/scrape/', views.LegalFrameworkScrapeView.as_view(), name='admin_framework_scrape'),
    path('admin/frameworks/<int:pk>/eliminar/', views.LegalFrameworkDeleteView.as_view(), name='admin_framework_delete'),
    path('admin/frameworks/generar-contenido/', views.LegalFrameworkGenerateContentView.as_view(), name='admin_framework_generate_ai'),
    
    # Actualización AJAX de la Ley 1715
    path('api/update-ley-1715/', views.update_ley_1715_view, name='update_ley_1715'),
    # Actualización AJAX de la Ley 2099
    path('api/update-ley-2099/', views.update_ley_2099_view, name='update_ley_2099'),
    
    # URLs existentes
    path('categoria/<slug:category_slug>/', views.CategoryView.as_view(), name='category'),
    path('documento/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('buscar/', views.LegalFrameworkSearchView.as_view(), name='search'),
]
