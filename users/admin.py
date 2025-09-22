from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import BaseUser, OfertanteProfile, OfertanteDocument


@admin.register(BaseUser)
class BaseUserAdmin(UserAdmin):
    model = BaseUser
    list_display = ("email", "user_type", "is_active", "is_staff", "is_verified", "verification_status")
    list_filter = ("user_type", "is_active", "is_verified", "is_staff")
    search_fields = ("email",)
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Info", {"fields": ("user_type", "is_verified", "verification_status")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password", "user_type"),
        }),
    )

@admin.register(OfertanteProfile)
class OfertanteProfileAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'user', 'contact_name', 'organization_type')
    search_fields = ('organization_name', 'cnpj', 'user__email')
    autocomplete_fields = ('user',)

@admin.register(OfertanteDocument)
class OfertanteDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'verified', 'uploaded_at')
    search_fields = ('user__email',)
    list_filter = ('document_type', 'verified')
    autocomplete_fields = ('user',)
