from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from decimal import Decimal
import math

from .models import SolarSystem, Location, Simulation
from .forms import SolarSystemForm

class SimulatorHomeView(TemplateView):
    """Vista principal del simulador solar"""
    template_name = 'simulator/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Simulador Solar'
        context['recent_systems'] = SolarSystem.objects.filter(
            is_active=True
        ).order_by('-created_at')[:6] if self.request.user.is_authenticated else []
        context['locations'] = Location.objects.filter(is_active=True)[:10]
        return context


class CreateSystemView(LoginRequiredMixin, CreateView):
    """Vista para crear un nuevo sistema solar"""
    model = SolarSystem
    form_class = SolarSystemForm
    template_name = 'simulator/create_system.html'
    success_url = reverse_lazy('simulator:home')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(
            self.request, 
            '¡Sistema solar creado exitosamente! Ahora puedes ejecutar simulaciones.'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Sistema Solar'
        return context


class SimulateView(LoginRequiredMixin, DetailView):
    """Vista para ejecutar simulación"""
    model = SolarSystem
    template_name = 'simulator/simulate.html'
    context_object_name = 'system'
    pk_url_kwarg = 'system_id'
    
    def get_queryset(self):
        return SolarSystem.objects.filter(user=self.request.user, is_active=True)
    
    def post(self, request, *args, **kwargs):
        """Ejecutar simulación"""
        system = self.get_object()
        
        # Cálculos de simulación
        daily_generation = system.estimated_daily_generation
        monthly_generation = daily_generation * 30
        
        # Tarifa promedio de energía en Colombia (COP/kWh)
        energy_rate = Decimal('600')  # $600 COP por kWh
        monthly_savings = monthly_generation * energy_rate
        
        # Factor de emisiones CO2 (kg CO2/kWh) para Colombia
        co2_factor = Decimal('0.164')  # kg CO2/kWh
        co2_avoided = monthly_generation * co2_factor
        
        # Período de retorno de inversión
        if monthly_savings > 0:
            payback_period = system.installation_cost / (monthly_savings * 12)
        else:
            payback_period = 0
        
        # Crear simulación
        simulation = Simulation.objects.create(
            solar_system=system,
            monthly_generation=monthly_generation,
            monthly_savings=monthly_savings,
            co2_avoided=co2_avoided,
            payback_period_years=payback_period
        )
        
        messages.success(
            request, 
            f'Simulación completada exitosamente. Tu sistema puede generar {monthly_generation:.2f} kWh al mes.'
        )
        
        return redirect('simulator:results', simulation_id=simulation.pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Simular - {self.object.name}'
        return context


class SimulationResultsView(LoginRequiredMixin, DetailView):
    """Vista para mostrar resultados de simulación"""
    model = Simulation
    template_name = 'simulator/results.html'
    context_object_name = 'simulation'
    pk_url_kwarg = 'simulation_id'
    
    def get_queryset(self):
        return Simulation.objects.filter(
            solar_system__user=self.request.user,
            is_active=True
        ).select_related('solar_system', 'solar_system__location')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Resultados de Simulación'
        
        # Cálculos adicionales para mostrar
        simulation = self.object
        context['annual_generation'] = simulation.monthly_generation * 12
        context['annual_savings'] = simulation.monthly_savings * 12
        context['annual_co2_avoided'] = simulation.co2_avoided * 12
        
        # Proyecciones a 25 años
        context['lifetime_generation'] = context['annual_generation'] * 25
        context['lifetime_savings'] = context['annual_savings'] * 25
        context['lifetime_co2_avoided'] = context['annual_co2_avoided'] * 25
        
        return context
