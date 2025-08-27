from rest_framework import serializers
from workspace.models import Workspace, Organization
from workspace.config.plans import PLAN_CHOICES


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "logo",
            "brand",
            "created_at",
            "updated_at",
        ]
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
        # Enforce unique workspace name per owner (creator)
        request = self.context.get("request")
        name = attrs.get("name")
        if request and name:
            exists = Workspace.objects.filter(owner=request.user, name=name).exists()
            if exists:
                raise serializers.ValidationError(
                    {"name": "You already have a workspace with this name."}
                )
        return attrs

    def create(self, validated_data):
        org_id = validated_data.pop("organization_id", None)
        org_data = validated_data.pop("organization", None)
        validated_data.pop("plan", None)
        request = self.context.get("request")
        org = None
        if org_id:
            try:
                org = Organization.objects.get(pk=org_id)
            except Organization.DoesNotExist:
                raise serializers.ValidationError("Organization not found.")
        elif org_data:
            # Assign owner to enforce per-user uniqueness; reuse existing if same name
            owner = request.user if request else None
            if owner:
                existing = Organization.objects.filter(
                    owner=owner, name=org_data.get("name")
                ).first()
                org = existing or Organization.objects.create(owner=owner, **org_data)
            else:
                org = Organization.objects.create(**org_data)
        ws = Workspace.objects.create(
            owner=request.user if request else None,
            organization=org,
            **validated_data,
        )
        return ws
