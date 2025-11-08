from django.contrib import admin
from django.db.models.functions import Now

from .models import BlogPost, BlogCategory, BlogImage, BlogComment, BlogReaction, BlogReport


class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 1
    max_num = 5


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [BlogImageInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    list_display = ('post', 'caption', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('caption', 'post__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'display_name', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('content', 'name', 'email', 'post__title')
    readonly_fields = ('created_at', 'updated_at')

    def display_name(self, obj):
        return obj.display_name
    display_name.short_description = 'Autor'


@admin.register(BlogReaction)
class BlogReactionAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('post__title', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BlogReport)
class BlogReportAdmin(admin.ModelAdmin):
    list_display = ('target_type', 'post', 'comment', 'reporter', 'status', 'created_at', 'processed_at')
    list_filter = ('target_type', 'status', 'created_at')
    search_fields = ('reason', 'post__title', 'comment__content')
    readonly_fields = ('created_at', 'updated_at', 'processed_at', 'processed_by')
    actions = ['mark_in_review', 'mark_resolved', 'mark_dismissed']

    def _update_status(self, request, queryset, status):
        count = queryset.update(status=status, processed_by=request.user, processed_at=Now())
        self.message_user(request, f"{count} reporte(s) marcados como {status.replace('_', ' ')}")

    def mark_in_review(self, request, queryset):
        self._update_status(request, queryset, 'in_review')
    mark_in_review.short_description = 'Marcar como en revisión'

    def mark_resolved(self, request, queryset):
        self._update_status(request, queryset, 'resolved')
    mark_resolved.short_description = 'Marcar como resueltos'

    def mark_dismissed(self, request, queryset):
        self._update_status(request, queryset, 'dismissed')
    mark_dismissed.short_description = 'Descartar reportes'
