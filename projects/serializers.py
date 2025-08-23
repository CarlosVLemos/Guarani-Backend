
from rest_framework import serializers
from .models import Project, Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "name", "file", "uploaded_at"]


class ProjectListSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id", "name", "project_type", "location",
            "latitude", "longitude",
            "carbon_credits_available", "price_per_credit",
            "status", "owner", "created_at", "updated_at",
        ]


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id", "name", "description", "project_type", "location",
            "latitude", "longitude",
            "carbon_credits_available", "price_per_credit",
            "status", "owner", "created_at", "updated_at",
            "documents",
        ]

    def validate(self, data):
        lat = data.get("latitude")
        lon = data.get("longitude")
        if lat is not None and (lat < -90 or lat > 90):
            raise serializers.ValidationError({"latitude": "Latitude deve estar entre -90 e 90."})
        if lon is not None and (lon < -180 or lon > 180):
            raise serializers.ValidationError({"longitude": "Longitude deve estar entre -180 e 180."})
        if data.get("price_per_credit", 0) < 0:
            raise serializers.ValidationError({"price_per_credit": "Preço não pode ser negativo."})
        return data

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)
