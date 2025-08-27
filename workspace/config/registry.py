from typing import Dict
from django.conf import settings
from importlib import import_module
from workspace.models import PermissionScope


def get_permissions_registry() -> Dict[str, PermissionScope]:
    modules = getattr(
        settings,
        "WORKSPACE_PERMISSION_MODULES",
        ["workspace.config.permissions"],
    )
    registry: Dict[str, PermissionScope] = {}
    for mod in modules:
        try:
            m = import_module(mod)
            perms = getattr(m, "PERMS", None)
            if isinstance(perms, dict):
                normalized: Dict[str, PermissionScope] = {}
                for k, v in perms.items():
                    key = k.value if hasattr(k, "value") else k  # Enum or str
                    if not isinstance(v, PermissionScope):
                        raise ValueError("Permission scope must be a PermissionScope")
                    if isinstance(key, str):
                        normalized[key] = v
                registry.update(normalized)
        except Exception:
            continue
    return registry
