
from django.contrib import admin
from .models import Project, Document


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "project_type", "status", "owner", "carbon_credits_available", "price_per_credit", "created_at")
    list_filter = ("status", "project_type", "owner")
    search_fields = ("name", "description", "location")
    autocomplete_fields = ("owner",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "project", "uploaded_at")
    search_fields = ("name",)
    autocomplete_fields = ("project",)
