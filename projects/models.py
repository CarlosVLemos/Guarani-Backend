
from django.conf import settings
from django.db import models
from django.utils import timezone


class ProjectQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(is_deleted=False)


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        VALIDATED = "VALIDATED", "Validated"

    name = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    project_type = models.CharField(max_length=100)
    location = models.CharField(max_length=180, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    carbon_credits_available = models.PositiveIntegerField(default=0)
    price_per_credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")

    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["project_type"]),
            models.Index(fields=["owner"]),
            models.Index(fields=["is_deleted"]),
        ]
        ordering = ["-created_at"]

    def soft_delete(self):
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])

    def __str__(self):
        return f"{self.name} ({self.status})"


def document_upload_to(instance, filename):
    # e.g. media/projects/<project_id>/<filename>
    return f"projects/{instance.project_id}/{filename}"


class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    name = models.CharField(max_length=180)
    file = models.FileField(upload_to=document_upload_to)
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
