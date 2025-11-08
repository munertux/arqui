from django.db import models
from apps.core.models import BaseModel
from apps.accounts.models import User

class Location(BaseModel):
    """Modelo para ubicaciones en Colombia"""
    name = models.CharField(max_length=100, verbose_name='Nombre')
    department = models.CharField(max_length=50, verbose_name='Departamento')
    city = models.CharField(max_length=50, verbose_name='Ciudad')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name='Latitud')
    longitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name='Longitud')
    solar_irradiance = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='Irradiación solar promedio (kWh/m²/día)'
    )
    
    class Meta:
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
        
    def __str__(self):
        return f"{self.city}, {self.department}"


class SolarSystem(BaseModel):
    """Modelo para sistemas solares"""
    
    SYSTEM_TYPES = [
        ('grid_tied', 'Conectado a la red'),
        ('off_grid', 'Aislado'),
        ('hybrid', 'Híbrido'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    name = models.CharField(max_length=100, verbose_name='Nombre del sistema')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name='Ubicación')
    system_type = models.CharField(max_length=20, choices=SYSTEM_TYPES, verbose_name='Tipo de sistema')
    panel_power = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Potencia por panel (W)')
    num_panels = models.IntegerField(verbose_name='Número de paneles')
    inverter_efficiency = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=95.00,
        verbose_name='Eficiencia del inversor (%)'
    )
    installation_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Costo de instalación (COP)'
    )
    monthly_consumption = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='Consumo mensual (kWh)'
    )
    
    class Meta:
        verbose_name = 'Sistema solar'
        verbose_name_plural = 'Sistemas solares'
        
    def __str__(self):
        return f"{self.name} - {self.user.full_name}"
    
    @property
    def total_power(self):
        """Potencia total del sistema en kW"""
        return (self.panel_power * self.num_panels) / 1000
    
    @property
    def estimated_daily_generation(self):
        """Generación diaria estimada en kWh"""
        if self.location:
            return (self.total_power * self.location.solar_irradiance * 
                   self.inverter_efficiency / 100)
        return 0
    
    @property
    def estimated_monthly_generation(self):
        """Generación mensual estimada en kWh"""
        return self.estimated_daily_generation * 30


class Simulation(BaseModel):
    """Modelo para simulaciones de sistemas solares"""
    solar_system = models.ForeignKey(
        SolarSystem, 
        on_delete=models.CASCADE, 
        verbose_name='Sistema solar'
    )
    simulation_date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de simulación')
    monthly_generation = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='Generación mensual (kWh)'
    )
    monthly_savings = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Ahorro mensual (COP)'
    )
    co2_avoided = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='CO2 evitado (kg)'
    )
    payback_period_years = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        verbose_name='Período de retorno (años)'
    )
    
    class Meta:
        verbose_name = 'Simulación'
        verbose_name_plural = 'Simulaciones'
        ordering = ['-simulation_date']
        
    def __str__(self):
        return f"Simulación {self.solar_system.name} - {self.simulation_date.strftime('%d/%m/%Y')}"
