from rest_framework import serializers


class CheckoutRequestSerializer(serializers.Serializer):
    plan = serializers.CharField(max_length=50)


class CheckoutResponseSerializer(serializers.Serializer):
    url = serializers.URLField()


class ConfirmRequestSerializer(serializers.Serializer):
    session_id = serializers.CharField()
