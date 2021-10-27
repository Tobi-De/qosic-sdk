"""Helpers functions that are used in main module"""

import json
import logging
from typing import List

from httpx import Response
from phonenumbers import PhoneNumber

from .exceptions import (
    ProviderNotFoundError,
)
from .models import Provider

logging.basicConfig(level=logging.DEBUG, format="%(message)s")


def get_json_response(response: Response) -> dict:
    default = {"responsecode": None}
    try:
        json_content = response.json()
    except json.decoder.JSONDecodeError:
        return default
    else:
        json_content = (
            json_content if json_content and isinstance(json_content, dict) else default
        )
        return json_content


def guess_provider(phone: PhoneNumber, providers: List[Provider]) -> Provider:
    prefixe = str(phone.national_number)[:2]
    for provider in providers:
        if prefixe in provider.allowed_prefixes:
            return provider
    raise ProviderNotFoundError(
        f"A provider was not found for the given phone number: {phone}"
    )
