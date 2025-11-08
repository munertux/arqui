from django.urls import path
from . import views

app_name = 'simulator'

urlpatterns = [
    path('', views.SimulatorHomeView.as_view(), name='home'),
    path('create/', views.CreateSystemView.as_view(), name='create_system'),
    path('simulate/<int:system_id>/', views.SimulateView.as_view(), name='simulate'),
    path('results/<int:simulation_id>/', views.SimulationResultsView.as_view(), name='results'),
]
