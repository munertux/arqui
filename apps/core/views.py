from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class HomeView(TemplateView):
    """Vista principal del sitio"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'SIESE - Sistema Integral de Energía Solar en Colombia'
        context['description'] = 'Plataforma web para simular, monitorear y aprender sobre energía solar en Colombia'
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """Panel principal después de iniciar sesión."""

    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            'page_title': 'Panel principal',
            'user_roles': user.roles.filter(is_active=True),
            'primary_role': user.get_role_display(),
            'quick_links': [
                {
                    'title': 'Simulador Solar',
                    'url': 'simulator:home',
                    'icon': 'fas fa-calculator',
                    'description': 'Corre simulaciones para planear tus proyectos.',
                },
                {
                    'title': 'Panel de Monitoreo',
                    'url': 'monitoring:dashboard',
                    'icon': 'fas fa-chart-line',
                    'description': 'Visualiza métricas de generación y ahorro.',
                },
                {
                    'title': 'Repositorio Normativo',
                    'url': 'regulatory:legal_framework_list',
                    'icon': 'fas fa-gavel',
                    'description': 'Consulta leyes, decretos y lineamientos vigentes.',
                },
                {
                    'title': 'Noticias del Sector',
                    'url': 'news:home',
                    'icon': 'fas fa-newspaper',
                    'description': 'Mantente al día con la transición energética.',
                },
            ],
        })
        return context
