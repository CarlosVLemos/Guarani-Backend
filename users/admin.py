from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OfertanteProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Define a interface de admin para o modelo User customizado."""
    list_display = ('email', 'user_type', 'is_staff', 'is_verified', 'verification_status', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email',)
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações da Plataforma', {'fields': ('user_type', 'is_verified', 'verification_status')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2', 'user_type'),
        }),
    )

@admin.register(OfertanteProfile)
class OfertanteProfileAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'user', 'contact_name', 'organization_type')
    search_fields = ('organization_name', 'cnpj', 'user__email')
    autocomplete_fields = ('user',)