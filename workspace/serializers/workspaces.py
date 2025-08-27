from rest_framework import serializers
from workspace.models import Workspace, Organization
from workspace.config.plans import PLAN_CHOICES


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "logo", "brand", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class WorkspaceSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(allow_null=True)

    class Meta:
        model = Workspace
        fields = [
            "id",
            "name",
            "owner",
            "organization",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]


class WorkspaceCreateSerializer(serializers.ModelSerializer):
    plan = serializers.ChoiceField(
        choices=PLAN_CHOICES, required=False, allow_null=True
    )
    # Either reuse an existing org by id, or create a minimal new org inline
    organization_id = serializers.UUIDField(required=False, allow_null=True)
    organization = OrganizationSerializer(required=False)

    class Meta:
        model = Workspace
        fields = ["name", "plan", "organization_id", "organization"]

    def validate(self, attrs):
        org_id = attrs.get("organization_id")
        org_data = attrs.get("organization")
        if org_id and org_data:
            raise serializers.ValidationError(
                "Provide either organization_id or organization, not both."
            )
        return attrs

    def create(self, validated_data):
        org_id = validated_data.pop("organization_id", None)
        org_data = validated_data.pop("organization", None)
        request = self.context.get("request")
        org = None
        if org_id:
            try:
                org = Organization.objects.get(pk=org_id)
            except Organization.DoesNotExist:
                raise serializers.ValidationError("Organization not found.")
        elif org_data:
            org = Organization.objects.create(**org_data)
        ws = Workspace.objects.create(
            owner=request.user if request else None,
            organization=org,
            **validated_data,
        )
        return ws
