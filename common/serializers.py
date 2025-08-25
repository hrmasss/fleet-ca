from rest_framework import serializers
import re


_ABSOLUTE_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


class FlexibleURLField(serializers.CharField):
    """Lenient URL field that accepts:

    - Absolute http/https URLs
    - Site-relative paths starting with '/'
    - Blank / null values (returned as empty string)

    This avoids strict URL validation failures in cases where the frontend
    expects either a fully-qualified URL or a relative path to be resolved
    client-side. Stored value is left unchanged (relative paths preserved).
    """

    default_error_messages = {
        "invalid": "Enter a valid absolute (http/https) or relative URL starting with '/'.",
    }

    def __init__(self, *args, allow_null=True, **kwargs):  # type: ignore[override]
        # We map null -> empty string for storage consistency.
        kwargs.setdefault("allow_blank", True)
        super().__init__(*args, **kwargs)
        self.allow_null = allow_null

    def to_internal_value(self, data):  # pragma: no cover - simple validation
        if data is None:
            if self.allow_null:
                return ""
            self.fail("invalid")
        if isinstance(data, str):
            data = data.strip()
            if data == "":
                return ""
            if data.startswith("/") or _ABSOLUTE_URL_RE.match(data):
                return data
        self.fail("invalid")

    def to_representation(self, value):  # pragma: no cover - passthrough
        if value in (None, ""):
            return ""
        return value


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField(
        help_text="A message to be returned in the response."
    )


class AbsoluteURLSerializerMixin:
    """Mixin that converts configured File/Image fields to absolute URLs.

    Set ``absolute_url_fields`` in subclasses to a list/tuple of field names
    that should be represented with a fully qualified URL. If the request
    isn't in context the field is left as-is (relative path), so views that
    manually instantiate serializers MUST pass ``context={'request': request}``
    for consistency.
    """

    absolute_url_fields: tuple[str, ...] | list[str] = ()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self.absolute_url_fields:
            return data
        request = self.context.get("request") if hasattr(self, "context") else None
        if not request:
            return data
        for field_name in self.absolute_url_fields:
            if field_name not in data:
                continue
            file_obj = getattr(instance, field_name, None)
            if not file_obj:
                continue
            try:
                url = file_obj.url
            except Exception:
                continue
            data[field_name] = request.build_absolute_uri(url)
        return data
