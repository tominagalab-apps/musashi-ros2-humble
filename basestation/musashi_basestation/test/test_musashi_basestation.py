import pytest

from musashi_basestation import add_one


def test_add_one():
    assert add_one(3) == 4
    assert add_one(-2) == -1