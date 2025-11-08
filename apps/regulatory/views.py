import json

from bs4 import BeautifulSoup
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib import messages
from django.http import JsonResponse
from openai import OpenAI

from .models import LegalFramework, RegulatoryCategory, RegulatoryDocument
from .services import update_ley_1715_data, update_ley_2099_data, update_legal_framework_entry, LegalScrapingService
from .forms import LegalFrameworkForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
import logging

logger = logging.getLogger(__name__)

class LegalFrameworkListView(ListView):
    """Lista todos los marcos legales disponibles"""
    model = LegalFramework
    template_name = 'regulatory/legal_framework_list.html'
    context_object_name = 'legal_frameworks'
    paginate_by = 12
    
    def get_queryset(self):
        return LegalFramework.objects.filter(is_active=True).select_related()


class LegalFrameworkDetailView(DetailView):
    """Detalle genérico para cualquier marco legal."""

    model = LegalFramework
    template_name = 'regulatory/legal_framework_detail.html'
    context_object_name = 'framework'

    def get_object(self):
        document_number = str(self.kwargs['document_number'])
        year = self.kwargs['year']
        document_type = self.kwargs.get('document_type')

        queryset = LegalFramework.objects.filter(
            document_number=document_number,
            year=year,
            is_active=True,
        )
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        return get_object_or_404(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        framework = context['framework']
        context.update({
            'page_title': f"{framework.title}",
            'meta_description': framework.summary[:150] if framework.summary else '',
            'show_update_button': self.request.user.is_staff,
            'pdf_url': self._build_pdf_url(framework.official_url),
        })
        return context

    @staticmethod
    def _build_pdf_url(official_url: str):
        if not official_url:
            return None

        from urllib.parse import urlparse, urlunparse

        parsed = urlparse(official_url)
        if not parsed.netloc:
            return None

        path = parsed.path or ''
        if 'norma_pdf.php' in path:
            return official_url
        if 'norma.php' in path:
            pdf_path = path.replace('norma.php', 'norma_pdf.php', 1)
            return urlunparse(parsed._replace(path=pdf_path))

        return None

def update_ley_1715_view(request):
    """Vista AJAX para actualizar información de la Ley 1715"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    if request.method == 'POST':
        try:
            ley, created = update_ley_1715_data()
            
            return JsonResponse({
                'success': True,
                'message': f'Ley 1715 {"creada" if created else "actualizada"} exitosamente',
                'last_updated': ley.last_scraped.isoformat() if ley.last_scraped else None,
                'title': ley.title
            })
            
        except Exception as e:
            logger.error(f"Error actualizando Ley 1715: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Error al actualizar la información'
            }, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def update_ley_2099_view(request):
    """Vista AJAX para actualizar información de la Ley 2099"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    if request.method == 'POST':
        try:
            ley, created = update_ley_2099_data()
            return JsonResponse({
                'success': True,
                'message': f'Ley 2099 {"creada" if created else "actualizada"} exitosamente',
                'last_updated': ley.last_scraped.isoformat() if ley.last_scraped else None,
                'title': ley.title
            })
        except Exception as e:
            logger.error(f"Error actualizando Ley 2099: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Error al actualizar la información'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Vistas existentes
class RegulatoryHomeView(TemplateView):
    """Vista principal del repositorio normativo"""
    template_name = 'regulatory/home.html'

class CategoryView(TemplateView):
    """Vista de categoría regulatoria"""
    template_name = 'regulatory/category.html'

class DocumentDetailView(TemplateView):
    """Vista de detalle del documento"""
    template_name = 'regulatory/document_detail.html'

class LegalFrameworkSearchView(ListView):
    """Búsqueda avanzada de marcos legales."""

    template_name = 'regulatory/search.html'
    context_object_name = 'results'
    paginate_by = 12

    def get_queryset(self):
        from django.db.models import Q, Value, IntegerField, Case, When

        qs = LegalFramework.objects.filter(is_active=True)

        q = (self.request.GET.get('q') or '').strip()
        year = (self.request.GET.get('year') or '').strip()
        entity = (self.request.GET.get('entity') or '').strip()
        ordering = (self.request.GET.get('ordering') or 'relevance').strip() or 'relevance'

        if year:
            qs = qs.filter(year=year)

        if entity:
            qs = qs.filter(issuing_entity__iexact=entity)

        if q:
            search_filter = (
                Q(title__icontains=q) |
                Q(summary__icontains=q) |
                Q(main_objective__icontains=q) |
                Q(benefits_companies__icontains=q) |
                Q(benefits_citizens__icontains=q)
            )
            qs = qs.filter(search_filter)

            relevance = (
                Case(When(title__icontains=q, then=Value(5)), default=Value(0), output_field=IntegerField()) +
                Case(When(summary__icontains=q, then=Value(3)), default=Value(0), output_field=IntegerField()) +
                Case(When(main_objective__icontains=q, then=Value(2)), default=Value(0), output_field=IntegerField()) +
                Case(When(benefits_companies__icontains=q, then=Value(1)), default=Value(0), output_field=IntegerField()) +
                Case(When(benefits_citizens__icontains=q, then=Value(1)), default=Value(0), output_field=IntegerField())
            )
            qs = qs.annotate(relevance=relevance)
        else:
            qs = qs.annotate(relevance=Value(0, output_field=IntegerField()))

        if ordering == 'date':
            qs = qs.order_by('-year', 'document_type', 'document_number')
        else:
            qs = qs.order_by('-relevance', '-year', 'document_type', 'document_number')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs_base = LegalFramework.objects.filter(is_active=True)
        context.update({
            'q': (self.request.GET.get('q') or '').strip(),
            'selected_year': (self.request.GET.get('year') or '').strip(),
            'selected_entity': (self.request.GET.get('entity') or '').strip(),
            'selected_ordering': (self.request.GET.get('ordering') or 'relevance').strip() or 'relevance',
            'available_years': qs_base.order_by('-year').values_list('year', flat=True).distinct(),
            'available_entities': qs_base.exclude(issuing_entity='').order_by('issuing_entity').values_list('issuing_entity', flat=True).distinct(),
        })
        return context


class AdminRoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restringe el acceso a usuarios con rol administrativo."""

    def test_func(self):
        return bool(self.request.user.is_authenticated and self.request.user.is_admin_role)

    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a la gestión regulatoria.')
        return redirect('core:dashboard')


class LegalFrameworkAdminListView(AdminRoleRequiredMixin, ListView):
    """Listado administrativo de marcos legales."""

    model = LegalFramework
    template_name = 'regulatory/admin/framework_list.html'
    context_object_name = 'frameworks'
    paginate_by = 20

    def get_queryset(self):
        return LegalFramework.objects.all().order_by('-year', 'document_number')


class LegalFrameworkCreateView(AdminRoleRequiredMixin, CreateView):
    """Permite crear un nuevo marco legal para habilitar el scraping."""

    model = LegalFramework
    form_class = LegalFrameworkForm
    template_name = 'regulatory/admin/framework_form.html'
    success_url = reverse_lazy('regulatory:admin_framework_list')

    def form_valid(self, form):
        messages.success(self.request, 'Marco legal creado. Ahora puedes ejecutar la actualización automática.')
        return super().form_valid(form)


class LegalFrameworkUpdateView(AdminRoleRequiredMixin, UpdateView):
    """Actualiza un marco legal existente."""

    model = LegalFramework
    form_class = LegalFrameworkForm
    template_name = 'regulatory/admin/framework_form.html'
    success_url = reverse_lazy('regulatory:admin_framework_list')

    def form_valid(self, form):
        messages.success(self.request, 'Información del marco legal actualizada correctamente.')
        return super().form_valid(form)


class LegalFrameworkScrapeView(AdminRoleRequiredMixin, View):
    """Ejecuta el scraping y actualización para un marco legal específico."""

    def post(self, request, pk):
        framework = get_object_or_404(LegalFramework, pk=pk)

        try:
            update_legal_framework_entry(
                document_type=framework.document_type,
                document_number=framework.document_number,
                year=framework.year,
                official_url=framework.official_url,
                defaults={
                    'title': framework.title,
                    'summary': framework.summary,
                    'main_objective': framework.main_objective,
                    'benefits_companies': framework.benefits_companies,
                    'benefits_citizens': framework.benefits_citizens,
                    'official_url': framework.official_url,
                },
            )
            messages.success(request, f'Se actualizó el contenido oficial de {framework.title}.')
        except ValueError as exc:
            messages.warning(request, str(exc))
        except Exception as exc:
            messages.error(request, f'No fue posible completar el scraping: {exc}')

        return redirect('regulatory:admin_framework_list')


class LegalFrameworkDeleteView(AdminRoleRequiredMixin, View):
    """Elimina un marco legal existente."""

    def post(self, request, pk):
        framework = get_object_or_404(LegalFramework, pk=pk)
        title = framework.title
        framework.delete()
        messages.success(request, f'Se eliminó "{title}" del repositorio normativo.')
        return redirect('regulatory:admin_framework_list')


class LegalFrameworkGenerateContentView(AdminRoleRequiredMixin, View):
    """Genera resúmenes y beneficios usando IA a partir de la fuente oficial."""

    def post(self, request):
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            payload = request.POST.dict()

        framework_id = payload.get('framework_id')
        official_url = (payload.get('official_url') or '').strip()
        document_number = (payload.get('document_number') or '').strip()
        document_type = (payload.get('document_type') or 'ley').strip() or 'ley'
        year = payload.get('year')

        framework = None
        if framework_id:
            framework = get_object_or_404(LegalFramework, pk=framework_id)
            official_url = official_url or framework.official_url
            document_number = document_number or framework.document_number
            document_type = document_type or framework.document_type
            year = year or framework.year

        if not official_url:
            return JsonResponse({'error': 'Debes proporcionar la URL oficial antes de generar contenido con IA.'}, status=400)

        if not document_number or not year:
            return JsonResponse({'error': 'Completa número de documento y año antes de generar contenido.'}, status=400)

        try:
            year_int = int(year)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'El año debe ser un número válido.'}, status=400)

        scraper = LegalScrapingService()
        scraped = scraper.scrape_norma_oficial(official_url, number=str(document_number), year=year_int)
        content_html = scraped.get('content_scraped') or ''

        if not content_html:
            return JsonResponse({'error': 'No se pudo obtener el contenido oficial para generar texto. Verifica la URL.'}, status=400)

        soup = BeautifulSoup(content_html, 'html.parser')
        content_text = soup.get_text(separator=' ', strip=True)
        content_text = content_text[:6000]

        if not settings.OPENAI_API_KEY:
            return JsonResponse({'error': 'No hay una API Key configurada para la generación con IA.'}, status=500)

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        system_prompt = (
            "Eres un analista legal colombiano. Elaboras resúmenes claros de instrumentos normativos y detallas sus objetivos "
            "y beneficios para empresas y ciudadanos. Siempre respondes en español neutro, tono profesional y en formato JSON." 
        )

        user_prompt = (
            "Responde exclusivamente con un objeto JSON siguiendo exactamente esta estructura: "
            "{\"summary\": \"...\", \"main_objective\": \"...\", \"benefits_companies\": \"...\", \"benefits_citizens\": \"...\"}. "
            "No agregues texto adicional fuera del JSON. Utiliza el texto oficial para redactar cada campo con máximo 3 párrafos por elemento. "
            "Texto fuente:\n\n"
            f"Tipo de documento: {document_type}\nNúmero: {document_number}\nAño: {year_int}\n\n{content_text}"
        )

        try:
            response = client.responses.create(
                model='gpt-4.1-2025-04-14',
                temperature=0.2,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            ai_output = (response.output_text or '').strip()
        except Exception as exc:  # noqa: broad-except
            logger.exception("OpenAI API error when generating legal summary")
            return JsonResponse({'error': f'La API de IA devolvió un error: {exc}'}, status=502)

        try:
            data = json.loads(ai_output)
        except json.JSONDecodeError:
            import re

            match = re.search(r"\{.*\}", ai_output, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                except json.JSONDecodeError:
                    logger.error("Parsed JSON fragment still invalid: %s", match.group(0)[:300])
                    return JsonResponse({'error': 'No fue posible interpretar la respuesta de la IA. Inténtalo de nuevo.'}, status=500)
            else:
                logger.error("IA response could not be parsed as JSON: %s", ai_output[:300])
                return JsonResponse({'error': 'No fue posible interpretar la respuesta de la IA. Inténtalo de nuevo.'}, status=500)

        required_keys = {'summary', 'main_objective', 'benefits_companies', 'benefits_citizens'}
        if not required_keys.issubset(data.keys()):
            return JsonResponse({'error': 'La respuesta de la IA no contiene todos los campos requeridos.'}, status=500)

        return JsonResponse({
            'summary': data['summary'],
            'main_objective': data['main_objective'],
            'benefits_companies': data['benefits_companies'],
            'benefits_citizens': data['benefits_citizens'],
        })
