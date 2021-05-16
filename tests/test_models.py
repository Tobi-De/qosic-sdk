import pytest
from pydantic import ValidationError

from qosic.constants import MTN_PREFIXES
from qosic.models import (
    Provider,
    MtnConfig,
    OPERATION_CONFIRMED,
    OPERATION_REJECTED,
    Result,
)
from qosic.utils import get_random_string


def test_provider():
    def bad_random_string_generator():
        return None

    def bad_random_string_generator2():
        return get_random_string()

    def bad_random_string_generator3():
        return get_random_string(length=3)

    def bad_random_string_generator4():
        return get_random_string(length=18)

    with pytest.raises(ValidationError):
        Provider(
            client_id="jean pierre",
            allowed_prefixes=MTN_PREFIXES,
            transref_factory=bad_random_string_generator,
        )
    with pytest.raises(ValidationError):
        Provider(
            client_id="jean pierre",
            allowed_prefixes=MTN_PREFIXES,
            transref_factory=bad_random_string_generator2,
        )
    with pytest.raises(ValidationError):
        Provider(
            client_id="jean pierre",
            allowed_prefixes=MTN_PREFIXES,
            transref_factory=bad_random_string_generator3,
        )
    with pytest.raises(ValidationError):
        Provider(
            client_id="jean pierre",
            allowed_prefixes=MTN_PREFIXES,
            transref_factory=bad_random_string_generator4,
        )


def test_mtn_config():
    with pytest.raises(ValidationError):
        MtnConfig(step="joo", timeout=30)

    with pytest.raises(ValidationError):
        MtnConfig(step=30, timeout=60, max_tries=6)

    with pytest.raises(ValidationError):
        MtnConfig(step=30, timeout=500, max_tries=6)


def test_result():
    result = Result(
        state=OPERATION_CONFIRMED,
        trans_ref=get_random_string(),
        client_id=get_random_string(),
    )
    assert result.state == OPERATION_CONFIRMED
