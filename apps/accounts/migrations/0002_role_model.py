from django.db import migrations, models
import django.utils.timezone


def create_default_roles(apps, schema_editor):
    Role = apps.get_model('accounts', 'Role')
    User = apps.get_model('accounts', 'User')

    roles_data = [
        ('admin', 'Administrador', 'Acceso total a la plataforma y capacidades de gestión.'),
        ('editor', 'Editor', 'Puede gestionar contenido y recursos educativos o regulatorios.'),
        ('client', 'Cliente/Usuario', 'Acceso a simulaciones, monitoreo y recursos informativos.'),
        ('analyst', 'Analista', 'Puede revisar métricas y generar reportes avanzados.'),
    ]

    role_map = {}
    for slug, name, description in roles_data:
        role, _ = Role.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'description': description,
                'is_active': True,
            },
        )
        role_map[slug] = role

    for user in User.objects.all():
        primary_slug = user.role or 'client'
        if primary_slug in role_map:
            user.roles.add(role_map[primary_slug])
        if user.is_superuser and 'admin' in role_map:
            user.roles.add(role_map['admin'])


def remove_default_roles(apps, schema_editor):
    Role = apps.get_model('accounts', 'Role')
    Role.objects.filter(slug__in=['admin', 'editor', 'client', 'analyst']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, help_text='Fecha y hora en que se creó el registro', verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Fecha y hora de la última actualización', verbose_name='Fecha de actualización')),
                ('is_active', models.BooleanField(default=True, help_text='Indica si el registro está activo', verbose_name='Activo')),
                ('slug', models.SlugField(unique=True, verbose_name='Identificador')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Nombre')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
            ],
            options={
                'verbose_name': 'Rol',
                'verbose_name_plural': 'Roles',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='user',
            name='roles',
            field=models.ManyToManyField(blank=True, related_name='users', to='accounts.role', verbose_name='Roles adicionales'),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('client', 'Cliente/Usuario'), ('editor', 'Editor'), ('admin', 'Administrador'), ('analyst', 'Analista')], default='client', max_length=10, verbose_name='Rol principal'),
        ),
        migrations.RunPython(create_default_roles, remove_default_roles),
    ]
