from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from enum import Enum
from string import ascii_letters, digits

from httpx import Response


def get_json_response(response: Response) -> dict:
    default = {"responsecode": None}
    try:
        json_content = response.json()
    except json.decoder.JSONDecodeError:
        return default
    return json_content if json_content and isinstance(json_content, dict) else default


@dataclass
class Result:
    """A helper class to summarize the responses from the server."""

    class Status(str, Enum):
        """A helper class that represents the state of your payment request."""

        CONFIRMED = "CONFIRMED"
        FAILED = "FAILED"

    status: Status
    reference: str
    client_id: str
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.status == self.Status.CONFIRMED


def get_random_string(length: int = 12) -> str:
    return "".join(secrets.choice(ascii_letters + digits) for _ in range(length))
