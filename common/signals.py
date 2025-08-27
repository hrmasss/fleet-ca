import logging
from pathlib import Path
from typing import Any, Dict


SENSITIVE_KEYS = {
    "password",
    "confirm_password",
    "old_password",
    "new_password",
    "token",
    "access",
    "refresh",
    "secret",
    "authorization",
    "api_key",
    "client_secret",
}


def _api_log_path() -> Path:
    base_dir = Path(__file__).resolve().parents[1]
    logs_dir = base_dir / "_logs"
    logs_dir.mkdir(exist_ok=True)
    api_log = logs_dir / "api.log"
    if not api_log.exists():
        api_log.touch()
    return api_log


def _mask_sensitive(data: Dict[str, Any]) -> Dict[str, Any]:
    # Shallow mask on well-known keys at top level
    out: Dict[str, Any] = {}
    for k, v in data.items():
        if isinstance(k, str) and k.lower() in SENSITIVE_KEYS:
            out[k] = "***FILTERED***"
        else:
            out[k] = v
    return out


def setup_api_logger_signal() -> bool:
    """Subscribe a listener to API_LOGGER_SIGNAL and configure a file handler.
    Returns True if subscription is successful, otherwise False.
    """
    try:
        from drf_api_logger import API_LOGGER_SIGNAL
    except Exception:
        return False

    api_logger = logging.getLogger("api_logger")

    # Ensure file handler to _logs/api.log
    file_handler = logging.FileHandler(str(_api_log_path()))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    )
    if not any(
        isinstance(h, logging.FileHandler)
        and getattr(h, "baseFilename", None) == file_handler.baseFilename
        for h in api_logger.handlers
    ):
        api_logger.addHandler(file_handler)
        api_logger.setLevel(logging.INFO)
        api_logger.propagate = False

    def log_to_file(**payload: Any) -> None:
        masked = _mask_sensitive(payload)
        api_logger.info(masked)

    if log_to_file not in API_LOGGER_SIGNAL.listen:
        API_LOGGER_SIGNAL.listen += log_to_file

    return True
