from django.db import models
from apps.core.models import BaseModel
from apps.simulator.models import SolarSystem

class EnergyReading(BaseModel):
    """Modelo para lecturas de energía"""
    solar_system = models.ForeignKey(
        SolarSystem, 
        on_delete=models.CASCADE, 
        verbose_name='Sistema solar'
    )
    reading_date = models.DateTimeField(verbose_name='Fecha de lectura')
    energy_generated = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='Energía generada (kWh)'
    )
    energy_consumed = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='Energía consumida (kWh)'
    )
    energy_exported = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0,
        verbose_name='Energía exportada (kWh)'
    )
    
    class Meta:
        verbose_name = 'Lectura de energía'
        verbose_name_plural = 'Lecturas de energía'
        ordering = ['-reading_date']
        
    def __str__(self):
        return f"{self.solar_system.name} - {self.reading_date.strftime('%d/%m/%Y')}"


class MonthlyReport(BaseModel):
    """Modelo para reportes mensuales"""
    solar_system = models.ForeignKey(
        SolarSystem, 
        on_delete=models.CASCADE, 
        verbose_name='Sistema solar'
    )
    year = models.IntegerField(verbose_name='Año')
    month = models.IntegerField(verbose_name='Mes')
    total_generated = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='Total generado (kWh)'
    )
    total_consumed = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='Total consumido (kWh)'
    )
    total_savings = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Ahorro total (COP)'
    )
    co2_avoided = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name='CO2 evitado (kg)'
    )
    
    class Meta:
        verbose_name = 'Reporte mensual'
        verbose_name_plural = 'Reportes mensuales'
        unique_together = ['solar_system', 'year', 'month']
        ordering = ['-year', '-month']
        
    def __str__(self):
        return f"{self.solar_system.name} - {self.month:02d}/{self.year}"
