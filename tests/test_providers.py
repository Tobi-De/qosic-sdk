# import pytest
# from pydantic import ValidationError
#
# from qosic.providers import MTN, MOOV
# from qosic.utils import get_random_string
#
#
# def test_provider():
#     def bad_random_string_generator():
#         return None
#
#     def bad_random_string_generator1():
#         return get_random_string(length=3)
#
#     def bad_random_string_generator2():
#         return get_random_string(length=18)
#
#     client_id = "fake client id"
#     with pytest.raises(ValidationError):
#         MTN(
#             client_id=client_id,
#             reference_factory=bad_random_string_generator,
#         )
#         MOOV(
#             client_id=client_id,
#             reference_factory=bad_random_string_generator,
#         )
#     with pytest.raises(ValidationError):
#         MTN(
#             client_id=client_id,
#             reference_factory=bad_random_string_generator1,
#         )
#         MOOV(
#             client_id=client_id,
#             reference_factory=bad_random_string_generator1,
#         )
#
#     with pytest.raises(ValidationError):
#         MTN(
#             client_id=client_id,
#             reference_factory=bad_random_string_generator2,
#         )
#         MOOV(
#             client_id=client_id,
#             reference_factory=bad_random_string_generator2,
#         )
#
#
# def test_mtn():
#     with pytest.raises(AssertionError):
#         MTN(step="joo", timeout=30, client_id="fake")
#
#     with pytest.raises(AssertionError):
#         MTN(step=30, timeout=60, max_tries=6, client_id="fake")
#
#     with pytest.raises(AssertionError):
#         MTN(step=30, timeout=500, max_tries=6, client_id="fake")
