from django.contrib import admin
from .models import Project, Document


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "project_type", "status", "ofertante", "carbon_credits_available", "price_per_credit", "validated_by", "validated_at", "created_at")
    list_filter = ("status", "project_type", "ofertante")
    search_fields = ("name", "description", "location", "ofertante__email") # Permite buscar pelo email do ofertante
    autocomplete_fields = ("ofertante",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "project", "uploaded_at")
    search_fields = ("name",)
    autocomplete_fields = ("project",)