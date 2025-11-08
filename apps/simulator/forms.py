from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML
from .models import SolarSystem, Location

class SolarSystemForm(forms.ModelForm):
    """Formulario para crear un sistema solar"""
    
    class Meta:
        model = SolarSystem
        fields = [
            'name', 'location', 'system_type', 'panel_power', 
            'num_panels', 'inverter_efficiency', 'installation_cost', 
            'monthly_consumption'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mi Sistema Solar'}),
            'system_type': forms.Select(attrs={'class': 'form-input'}),
            'panel_power': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '450'}),
            'num_panels': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '10'}),
            'inverter_efficiency': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '95.00'}),
            'installation_cost': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '15000000'}),
            'monthly_consumption': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '300'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<div class="bg-white rounded-lg shadow-md p-6 mb-6">'),
            HTML('<h3 class="text-xl font-bold text-gray-900 mb-4">Información General</h3>'),
            Row(
                Column('name', css_class='form-group col-md-6 mb-4'),
                Column('location', css_class='form-group col-md-6 mb-4'),
            ),
            Row(
                Column('system_type', css_class='form-group col-md-12 mb-4'),
            ),
            HTML('</div>'),
            
            HTML('<div class="bg-white rounded-lg shadow-md p-6 mb-6">'),
            HTML('<h3 class="text-xl font-bold text-gray-900 mb-4">Especificaciones Técnicas</h3>'),
            Row(
                Column('panel_power', css_class='form-group col-md-6 mb-4'),
                Column('num_panels', css_class='form-group col-md-6 mb-4'),
            ),
            Row(
                Column('inverter_efficiency', css_class='form-group col-md-6 mb-4'),
                Column('monthly_consumption', css_class='form-group col-md-6 mb-4'),
            ),
            HTML('</div>'),
            
            HTML('<div class="bg-white rounded-lg shadow-md p-6 mb-6">'),
            HTML('<h3 class="text-xl font-bold text-gray-900 mb-4">Información Económica</h3>'),
            Row(
                Column('installation_cost', css_class='form-group col-md-12 mb-4'),
            ),
            HTML('</div>'),
            
            Submit('submit', 'Crear Sistema Solar', css_class='btn-solar w-full py-3 text-lg')
        )


class LocationForm(forms.ModelForm):
    """Formulario para crear ubicaciones"""
    
    class Meta:
        model = Location
        fields = ['name', 'department', 'city', 'latitude', 'longitude', 'solar_irradiance']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'department': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.0000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.0000001'}),
            'solar_irradiance': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
        }
