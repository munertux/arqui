from django.core.management.base import BaseCommand
from apps.simulator.models import Location

class Command(BaseCommand):
    help = 'Cargar ubicaciones principales de Colombia con datos de irradiación solar'

    def handle(self, *args, **options):
        locations = [
            {
                'name': 'Bogotá Centro',
                'department': 'Cundinamarca',
                'city': 'Bogotá',
                'latitude': 4.60971,
                'longitude': -74.08175,
                'solar_irradiance': 4.5,
            },
            {
                'name': 'Medellín Centro',
                'department': 'Antioquia',
                'city': 'Medellín',
                'latitude': 6.25184,
                'longitude': -75.56359,
                'solar_irradiance': 5.2,
            },
            {
                'name': 'Cali Centro',
                'department': 'Valle del Cauca',
                'city': 'Cali',
                'latitude': 3.43722,
                'longitude': -76.5225,
                'solar_irradiance': 5.8,
            },
            {
                'name': 'Barranquilla Centro',
                'department': 'Atlántico',
                'city': 'Barranquilla',
                'latitude': 10.96854,
                'longitude': -74.78132,
                'solar_irradiance': 6.2,
            },
            {
                'name': 'Cartagena Centro',
                'department': 'Bolívar',
                'city': 'Cartagena',
                'latitude': 10.39972,
                'longitude': -75.51444,
                'solar_irradiance': 6.1,
            },
            {
                'name': 'Bucaramanga Centro',
                'department': 'Santander',
                'city': 'Bucaramanga',
                'latitude': 7.11392,
                'longitude': -73.1198,
                'solar_irradiance': 5.0,
            },
            {
                'name': 'Pereira Centro',
                'department': 'Risaralda',
                'city': 'Pereira',
                'latitude': 4.81333,
                'longitude': -75.69611,
                'solar_irradiance': 4.8,
            },
            {
                'name': 'Santa Marta Centro',
                'department': 'Magdalena',
                'city': 'Santa Marta',
                'latitude': 11.24079,
                'longitude': -74.19904,
                'solar_irradiance': 6.3,
            },
            {
                'name': 'Ibagué Centro',
                'department': 'Tolima',
                'city': 'Ibagué',
                'latitude': 4.43889,
                'longitude': -75.23222,
                'solar_irradiance': 5.1,
            },
            {
                'name': 'Villavicencio Centro',
                'department': 'Meta',
                'city': 'Villavicencio',
                'latitude': 4.14208,
                'longitude': -73.63654,
                'solar_irradiance': 5.4,
            },
        ]

        for location_data in locations:
            location, created = Location.objects.get_or_create(
                city=location_data['city'],
                department=location_data['department'],
                defaults=location_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Ubicación creada: {location.city}, {location.department}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Ubicación ya existe: {location.city}, {location.department}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado. Total de ubicaciones en la base de datos: {Location.objects.count()}'
            )
        )
