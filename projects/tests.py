from django.test import TestCase
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from users.models import BaseUser
from .models import Project


class ProjectApprovalFlowTests(TestCase):
	def setUp(self):
		self.client = APIClient()

		# Cria grupo auditor
		self.auditor_group, _ = Group.objects.get_or_create(name="auditor")

		# Cria ofertante (dono do projeto)
		self.ofertante = BaseUser.objects.create_user(
			email="ofertante@example.com",
			password="Test#123",
			user_type=BaseUser.UserType.OFERTANTE,
		)

		# Cria auditor e adiciona ao grupo
		self.auditor = BaseUser.objects.create_user(
			email="auditor@example.com",
			password="Test#123",
			user_type=BaseUser.UserType.COMPRADOR,  # tipo não impacta o grupo
		)
		self.auditor.groups.add(self.auditor_group)

		# Cria projeto em DRAFT
		self.project = Project.objects.create(
			ofertante=self.ofertante,
			name="Projeto Teste",
			project_type=Project.ProjectType.OUTRO,
			status=Project.Status.DRAFT,
			carbon_credits_available=100,
			price_per_credit=10,
		)

	def test_non_auditor_cannot_validate(self):
		self.client.force_authenticate(user=self.ofertante)
		url = reverse("project-validate-project", kwargs={"pk": str(self.project.id)})
		res = self.client.post(url)
		self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

	def test_auditor_validates_and_owner_activates(self):
		# Auditor valida
		self.client.force_authenticate(user=self.auditor)
		url_validate = reverse("project-validate-project", kwargs={"pk": str(self.project.id)})
		res_val = self.client.post(url_validate)
		self.assertEqual(res_val.status_code, status.HTTP_200_OK)
		self.project.refresh_from_db()
		self.assertEqual(self.project.status, Project.Status.VALIDATED)
		self.assertIsNotNone(self.project.validated_by)
		self.assertIsNotNone(self.project.validated_at)

		# Dono ativa
		self.client.force_authenticate(user=self.ofertante)
		url_activate = reverse("project-activate-project", kwargs={"pk": str(self.project.id)})
		res_act = self.client.post(url_activate)
		self.assertEqual(res_act.status_code, status.HTTP_200_OK)
		self.project.refresh_from_db()
		self.assertEqual(self.project.status, Project.Status.ACTIVE)
