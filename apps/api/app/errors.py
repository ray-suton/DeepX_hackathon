from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PaladinError(Exception):
    code: str
    message: str
    user_action: str
    details: dict[str, Any] = field(default_factory=dict)
    status_code: int = 400

    def __post_init__(self) -> None:
        super().__init__(self.message)


class InvalidInputError(PaladinError):
    def __init__(self, message: str, user_action: str, details: dict[str, Any] | None = None):
        super().__init__("INVALID_INPUT", message, user_action, details or {}, 422)


class InvalidUploadError(PaladinError):
    def __init__(self, message: str, user_action: str, details: dict[str, Any] | None = None):
        super().__init__("INVALID_UPLOAD", message, user_action, details or {}, 422)


class ParseFailedError(PaladinError):
    def __init__(self, message: str, user_action: str, details: dict[str, Any] | None = None):
        super().__init__("PARSE_FAILED", message, user_action, details or {}, 400)


class UnsupportedModelError(PaladinError):
    def __init__(self, message: str, user_action: str, details: dict[str, Any] | None = None):
        super().__init__("UNSUPPORTED_MODEL", message, user_action, details or {}, 400)


class EstimationFailedError(PaladinError):
    def __init__(self, message: str, user_action: str, details: dict[str, Any] | None = None):
        super().__init__("ESTIMATION_FAILED", message, user_action, details or {}, 500)


def error_payload(exc: PaladinError) -> dict[str, Any]:
    payload = {
        "status": "error",
        "error": {
            "code": exc.code,
            "message": exc.message,
            "user_action": exc.user_action,
        },
    }
    if exc.details:
        payload["error"]["details"] = exc.details
    return payload

