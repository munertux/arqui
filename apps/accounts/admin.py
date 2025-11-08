from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, Role


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'roles', 'is_staff', 'is_active', 'is_email_verified')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    filter_horizontal = ('roles',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('role', 'roles', 'phone', 'location', 'is_email_verified')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('email', 'role', 'roles', 'phone', 'location')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'website', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'company')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
