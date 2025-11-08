from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, CreateView, View

from .forms import BlogPostForm, BlogImageFormSet, BlogCommentForm, BlogReportForm
from .models import BlogPost, BlogCategory, BlogComment, BlogReaction, BlogReport


class AdminRoleRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin_role', False):
            return redirect('core:dashboard') if request.user.is_authenticated else redirect('account_login')
        return super().dispatch(request, *args, **kwargs)


class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        qs = BlogPost.objects.filter(is_active=True).select_related('category', 'author').prefetch_related('images')
        qs = qs.annotate(
            comment_count=Count('comments', filter=Q(comments__is_active=True), distinct=True),
            reaction_count=Count('reactions', distinct=True)
        )

        ordering = (self.request.GET.get('ordering') or 'recent').strip()
        search = (self.request.GET.get('q') or '').strip()

        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )

        if ordering == 'popular':
            qs = qs.order_by('-comment_count', '-reaction_count', '-created_at')
        else:
            qs = qs.order_by('-created_at')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'selected_ordering': (self.request.GET.get('ordering') or 'recent').strip() or 'recent',
            'search_query': (self.request.GET.get('q') or '').strip(),
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            posts_html = render_to_string('blog/_post_cards.html', context, request=self.request)
            pagination_html = render_to_string('blog/_post_pagination.html', context, request=self.request)
            return JsonResponse({
                'posts_html': posts_html,
                'pagination_html': pagination_html,
            })
        return super().render_to_response(context, **response_kwargs)


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return BlogPost.objects.filter(is_active=True).select_related('category', 'author').prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']
        context['comment_form'] = BlogCommentForm(user=self.request.user)
        context['comments'] = post.comments.filter(is_active=True, parent__isnull=True).select_related('author').prefetch_related('replies__author', 'replies__replies__author')
        context['comment_count'] = post.comments.filter(is_active=True).count()
        context['reaction_count'] = post.reactions.count()
        context['user_has_reacted'] = False
        if self.request.user.is_authenticated:
            context['user_has_reacted'] = post.reactions.filter(user=self.request.user, reaction_type='like').exists()
        context['report_form'] = BlogReportForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.POST.get('action') == 'report_comment':
            return self.handle_comment_report(request)

        form = BlogCommentForm(request.POST, user=request.user)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            if request.user.is_authenticated:
                comment.author = request.user
                comment.name = request.user.get_full_name() or request.user.email
                comment.email = request.user.email

            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent = BlogComment.objects.filter(pk=parent_id, post=self.object).first()
                if parent:
                    comment.parent = parent

            comment.save()
            messages.success(request, 'Comentario publicado correctamente.')
            return redirect(f"{self.object.get_absolute_url()}#comentarios")

        context = self.get_context_data()
        context['comment_form'] = form
        messages.error(request, 'No pudimos publicar tu comentario. Revisa los campos resaltados.')
        return self.render_to_response(context)

    def handle_comment_report(self, request):
        comment_id = request.POST.get('comment_id')
        reason = (request.POST.get('reason') or '').strip()
        comment = get_object_or_404(BlogComment, pk=comment_id, post=self.object, is_active=True)
        if not reason:
            return JsonResponse({'success': False, 'error': 'Describe el motivo del reporte.'}, status=400)

        report = BlogReport.objects.create(
            target_type='comment',
            post=self.object,
            comment=comment,
            reporter=request.user if request.user.is_authenticated else None,
            reason=reason,
        )
        return JsonResponse({'success': True})


class BlogPostToggleReactionView(LoginRequiredMixin, View):
    def post(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug, is_active=True)
        reaction, created = BlogReaction.objects.get_or_create(post=post, user=request.user, defaults={'reaction_type': 'like'})
        if not created:
            reaction.delete()
            reacted = False
        else:
            reacted = True
        return JsonResponse({'reacted': reacted, 'count': post.reactions.count()})


class BlogPostReportView(View):
    def post(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug, is_active=True)
        form = BlogReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.target_type = 'post'
            report.post = post
            report.comment = None
            if request.user.is_authenticated:
                report.reporter = request.user
            report.save()
            messages.success(request, 'Gracias por tu reporte. Revisaremos el contenido.')
        else:
            messages.error(request, 'No pudimos enviar el reporte. Revisa el formulario.')
        return redirect(post.get_absolute_url() + '#comentarios')


class BlogReportListView(AdminRoleRequiredMixin, ListView):
    model = BlogReport
    template_name = 'blog/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20

    def get_queryset(self):
        status = (self.request.GET.get('status') or 'pending').strip()
        qs = BlogReport.objects.select_related('post', 'comment', 'reporter', 'processed_by')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-created_at')

    def post(self, request, *args, **kwargs):
        if not request.POST.get('report_id'):
            return redirect('blog:report_list')

        report = get_object_or_404(BlogReport, pk=request.POST['report_id'])
        action = request.POST.get('action')
        new_status = None
        if action == 'in_review':
            new_status = 'in_review'
        elif action == 'resolved':
            new_status = 'resolved'
        elif action == 'dismissed':
            new_status = 'dismissed'

        if new_status:
            report.status = new_status
            report.processed_by = request.user
            from django.utils import timezone
            report.processed_at = timezone.now()
            report.save(update_fields=['status', 'processed_by', 'processed_at'])
            messages.success(request, f'Reporte #{report.id} marcado como {report.get_status_display().lower()}.')
        else:
            messages.error(request, 'Acción inválida para el reporte.')

        return redirect(request.path + f"?status={request.GET.get('status', 'pending')}")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_status_choices'] = BlogReport.STATUS_CHOICES
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_status_choices'] = BlogReport.STATUS_CHOICES
        return context


class BlogPostCreateView(LoginRequiredMixin, CreateView):
    model = BlogPost
    template_name = 'blog/post_form.html'
    form_class = BlogPostForm
    success_url = reverse_lazy('blog:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = BlogImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['image_formset'] = BlogImageFormSet()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        base_slug = slugify(form.instance.title) or 'publicacion'

        candidate = base_slug
        counter = 1
        while BlogPost.objects.filter(slug=candidate).exists():
            counter += 1
            candidate = f"{base_slug}-{counter}"

        form.instance.slug = candidate

        image_formset = BlogImageFormSet(self.request.POST, self.request.FILES)
        if image_formset.is_valid():
            images_total = len([f for f in image_formset.cleaned_data if f and not f.get('DELETE')])
            if images_total > 5:
                form.add_error(None, 'Solo puedes subir hasta 5 imágenes por publicación.')
                return self.form_invalid(form)
        else:
            form.add_error(None, 'Revisa los campos de las imágenes adjuntas.')
            return self.form_invalid(form)

        self.object = form.save()
        image_formset.instance = self.object
        image_formset.save()

        messages.success(self.request, 'Tu experiencia se publicó correctamente.')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'No pudimos guardar la publicación. Revisa los campos resaltados.')
        return super().form_invalid(form)
