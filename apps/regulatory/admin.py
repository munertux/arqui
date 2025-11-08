from django.contrib import admin
from .models import LegalFramework, ScrapingSource, RegulatoryCategory, RegulatoryDocument

@admin.register(LegalFramework)
class LegalFrameworkAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'document_number', 'year', 'issuing_entity', 'is_active', 'last_scraped']
    list_filter = ['document_type', 'year', 'issuing_entity', 'is_active', 'created_at']
    search_fields = ['title', 'document_number', 'summary', 'issuing_entity']
    readonly_fields = ['content_scraped', 'last_scraped', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'document_type', 'document_number', 'year', 'issuing_entity')
        }),
        ('Contenido', {
            'fields': ('summary', 'main_objective', 'benefits_companies', 'benefits_citizens')
        }),
        ('Enlaces y Fuentes', {
            'fields': ('official_url', 'content_scraped', 'last_scraped')
        }),
        ('Estado', {
            'fields': ('is_active', 'created_at', 'updated_at')
        })
    )
    
    actions = ['activate_items', 'deactivate_items']
    
    def activate_items(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} elementos activados.")
    activate_items.short_description = "Activar elementos seleccionados"
    
    def deactivate_items(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} elementos desactivados.")
    deactivate_items.short_description = "Desactivar elementos seleccionados"

@admin.register(ScrapingSource)
class ScrapingSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_url', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'base_url']

@admin.register(RegulatoryCategory)
class RegulatoryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']

@admin.register(RegulatoryDocument)
class RegulatoryDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'document_type', 'is_active', 'created_at']
    list_filter = ['category', 'document_type', 'is_active', 'created_at']
    search_fields = ['title', 'description']
