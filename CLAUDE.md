# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

qosic-sdk is an unofficial Python SDK for the QosIC platform, which provides APIs for mobile money payments in Africa (specifically Benin). The SDK supports MTN and MOOV mobile carriers.

## Development Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_api.py

# Run a specific test
uv run pytest tests/test_api.py::test_request_payment_mtn_ok_response

# Run tests with coverage
uv run coverage run -m pytest && uv run coverage report

# Type checking
uv run mypy qosic

# Code formatting
uv run black qosic tests

# Build documentation with live reload
uv run sphinx-watch docs docs/_build html --httpd --port 8080
```

## Architecture

### Core Components

- **`qosic/client.py`**: Main `Client` class that handles payment and refund requests. Uses httpx for HTTP communication with the QosIC API. The client auto-detects which mobile carrier to use based on phone number prefix.

- **`qosic/protocols.py`**: Defines the `MobileCarrier` protocol that all carrier implementations must follow (pay/refund methods, allowed_prefixes, reference_factory).

- **`qosic/utils.py`**: Contains `Result` (payment result dataclass), `Payer` (payer info with phone validation), and utility functions like `guess_mobile_carrier_from()` which matches phone prefixes to carriers.

### Mobile Carriers (`qosic/mobile_carriers/`)

Country-specific carrier implementations are organized by country code:

- **`bj/` (Benin)**: Contains `MTN` and `MOOV` classes
  - `MTN`: Implements payment with async status polling (uses polling2 library). Supports configurable timeout (60-180s), step interval (5-30s), and max_tries.
  - `MOOV`: Simpler synchronous payment. Does not support refunds (`FeatureNotImplementedError`).

Each carrier uses phone number prefixes to identify which carrier handles a given number.

### Error Handling (`qosic/errors.py`)

Custom exceptions for specific API errors:
- `ServerError`: QosIC server failures
- `InvalidCredentialsError`: Bad login/password
- `InvalidProviderIDError`: Bad carrier client ID
- `UserAccountNotFoundError`: Mobile money account not found
- `MobileCarrierNotFoundError`: Phone prefix doesn't match any configured carrier
- `InvalidPhoneNumberError`: Phone number format validation failure

### Testing

Tests use pytest-httpx to mock HTTP responses. The test fixtures create clients with random credentials and test against mocked QosIC API endpoints.

Phone numbers must be 11 digits in format `229XXXXXXXX` (229 is Benin country code).
