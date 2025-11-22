from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Crea (o actualiza) un usuario local de prueba con credenciales simples."

    def add_arguments(self, parser):
        parser.add_argument('--email', default='demo@example.com', help='Email del usuario (default: demo@example.com)')
        parser.add_argument('--username', default='demo', help='Username (default: demo)')
        parser.add_argument('--password', default='demo1234', help='Contraseña en texto plano (default: demo1234)')
        parser.add_argument('--role', default='client', help='Rol primario (default: client)')

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        username = options['username'].strip()
        password = options['password']
        role = options['role']

        user, created = User.objects.get_or_create(email=email, defaults={'username': username, 'role': role})
        if not created:
            user.username = username
            user.role = role
        user.set_password(password)
        user.save()

        msg_action = 'Creado' if created else 'Actualizado'
        self.stdout.write(self.style.SUCCESS(f'{msg_action} usuario local: {email} / {username}'))
        self.stdout.write(self.style.WARNING(f'Password en texto plano usado: {password}'))
        self.stdout.write('Puedes iniciar sesión ahora con esas credenciales.')
