import pytest

from qosic.mobile_carriers import bj
from qosic.utils import get_random_string


def test_provider():
    def bad_random_string_generator():
        return None

    def bad_random_string_generator1():
        return get_random_string(length=3)

    def bad_random_string_generator2():
        return get_random_string(length=18)

    client_id = "fake client id"
    with pytest.raises(AssertionError):
        bj.MTN(
            id=client_id,
            reference_factory=bad_random_string_generator,
        )
        bj.MOOV(
            id=client_id,
            reference_factory=bad_random_string_generator,
        )
    with pytest.raises(AssertionError):
        bj.MTN(
            id=client_id,
            reference_factory=bad_random_string_generator1,
        )
        bj.MOOV(
            id=client_id,
            reference_factory=bad_random_string_generator1,
        )

    with pytest.raises(AssertionError):
        bj.MTN(
            id=client_id,
            reference_factory=bad_random_string_generator2,
        )
        bj.MOOV(
            id=client_id,
            reference_factory=bad_random_string_generator2,
        )


def test_mtn():
    with pytest.raises(TypeError):
        bj.MTN(step="joo", timeout=30, id="fake")

    with pytest.raises(AssertionError):
        bj.MTN(step=30, timeout=60, max_tries=6, id="fake")

    with pytest.raises(AssertionError):
        bj.MTN(step=30, timeout=500, max_tries=6, id="fake")
