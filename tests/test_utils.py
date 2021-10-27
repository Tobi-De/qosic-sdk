from qosic.models import get_random_string, ALLOWED_STRING_CHARS


def test_get_random_string():
    random_string = get_random_string()
    assert isinstance(random_string, str)
    for char in random_string:
        assert char in ALLOWED_STRING_CHARS
