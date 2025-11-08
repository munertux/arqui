from django.contrib import admin
from .models import Location, SolarSystem, Simulation

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'department', 'solar_irradiance', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('name', 'city', 'department')
    ordering = ('department', 'city')

@admin.register(SolarSystem)
class SolarSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'location', 'system_type', 'total_power', 'created_at')
    list_filter = ('system_type', 'location__department', 'is_active')
    search_fields = ('name', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('total_power', 'estimated_daily_generation', 'estimated_monthly_generation')
    ordering = ('-created_at',)

@admin.register(Simulation)
class SimulationAdmin(admin.ModelAdmin):
    list_display = ('solar_system', 'simulation_date', 'monthly_generation', 'monthly_savings', 'co2_avoided')
    list_filter = ('simulation_date', 'is_active')
    search_fields = ('solar_system__name', 'solar_system__user__email')
    readonly_fields = ('simulation_date',)
    ordering = ('-simulation_date',)
