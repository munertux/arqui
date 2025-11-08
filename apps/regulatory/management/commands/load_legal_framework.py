from django.core.management.base import BaseCommand, CommandError

from apps.regulatory.models import LegalFramework
from apps.regulatory.services import update_legal_framework_entry


class Command(BaseCommand):
    help = (
        'Actualiza marcos legales existentes mediante scraping usando la URL oficial registrada. '
        'Permite ejecutar un único comando en lugar de mantener comandos por cada ley.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--document-type',
            dest='document_type',
            help='Tipo del documento (ej. ley, decreto, resolucion).'
        )
        parser.add_argument(
            '--document-number',
            dest='document_number',
            help='Número del documento (ej. 1715).'
        )
        parser.add_argument(
            '--year',
            dest='year',
            type=int,
            help='Año de expedición del documento.'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Actualiza todos los marcos legales con URL oficial configurada.'
        )

    def handle(self, *args, **options):
        document_type = options.get('document_type')
        document_number = options.get('document_number')
        year = options.get('year')
        update_all = options.get('all')

        targets = self._resolve_targets(document_type, document_number, year, update_all)

        updated = 0
        for framework in targets:
            self.stdout.write(f'🔄 Actualizando {framework}...')

            if not framework.official_url:
                self.stderr.write(
                    self.style.WARNING(
                        f'⚠️  {framework}: no tiene URL oficial configurada. Edítalo en el CRUD antes de actualizar.'
                    )
                )
                continue

            try:
                update_legal_framework_entry(
                    document_type=framework.document_type,
                    document_number=framework.document_number,
                    year=framework.year,
                    official_url=framework.official_url,
                )
            except ValueError as exc:
                self.stderr.write(self.style.WARNING(f'⚠️  {framework}: {exc}'))
                continue
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'❌ {framework}: {exc}'))
                continue

            updated += 1
            self.stdout.write(self.style.SUCCESS(f'✅ {framework} actualizado.'))

        if updated == 0:
            self.stdout.write(self.style.WARNING('No se actualizaron registros.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Se actualizaron {updated} registro(s).'))

    def _resolve_targets(self, document_type, document_number, year, update_all):
        queryset = LegalFramework.objects.all()

        if update_all:
            if document_type:
                queryset = queryset.filter(document_type=document_type)
            if document_number:
                queryset = queryset.filter(document_number=str(document_number))
            if year:
                queryset = queryset.filter(year=year)

            queryset = queryset.exclude(official_url__isnull=True).exclude(official_url__exact='')

            targets = list(queryset)
            if not targets:
                raise CommandError(
                    'No se encontraron marcos legales con los filtros proporcionados y URL oficial configurada.'
                )
            return targets

        # Para una actualización específica se requieren todos los parámetros
        missing = [
            name for name, value in [
                ('--document-type', document_type),
                ('--document-number', document_number),
                ('--year', year),
            ] if not value
        ]

        if missing:
            raise CommandError(
                'Debe indicar --document-type, --document-number y --year para actualizar un único registro, '
                'o usar la opción --all.'
            )

        try:
            framework = LegalFramework.objects.get(
                document_type=document_type,
                document_number=str(document_number),
                year=year,
            )
        except LegalFramework.DoesNotExist as exc:
            raise CommandError(
                'No existe un marco legal con los parámetros proporcionados. '
                'Cree el registro mediante el CRUD antes de ejecutar este comando.'
            ) from exc

        if not framework.official_url:
            raise CommandError(
                'El marco legal seleccionado no tiene URL oficial configurada. '
                'Edítelo desde el CRUD antes de actualizar.'
            )

        return [framework]
