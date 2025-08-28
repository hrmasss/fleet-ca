import os
from typing import Any, Optional

try:
    from constance import config as constance_config
except Exception:
    constance_config = None


def get(setting: str, default: Any | None = None) -> Any:
    """Return a dynamic setting from Constance, falling back to env or default. rder: Constance (if available) -> os.environ -> default"""
    if constance_config is not None and hasattr(constance_config, setting):
        value = getattr(constance_config, setting)
        if value not in (None, ""):
            return value
    value = os.getenv(setting)
    return value if value not in (None, "") else default


def get_bool(setting: str, default: bool = False) -> bool:
    val = get(setting)
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in {"1", "true", "yes", "on"}
    return bool(val) if val is not None else default


def get_secret(setting: str, default: Optional[str] = None) -> Optional[str]:
    """Return sensitive value. Pluggable for encryption later.

    TODO: Before production, implement transparent decrypt here when values
    are stored encrypted in Constance.
    """
    return get(setting, default)
