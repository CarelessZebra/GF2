import pytest
from names import Names

@pytest.fixture
def new_names():
    """Return a new names instance"""
    return Names()

@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["Alice", "Bob", "Eve"]

@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    my_names = Names()
    my_names.lookup(name_string_list)
    return my_names

@pytest.mark.parametrize("input_lists, expected_ids", [
    (["Alice", "Bob", "Eve"], [0, 1, 2]),
    (["Charlie", "Dave"], [3, 4]),
    (["Alice", "Charlie", "Dave"], [0, 3, 4]),
    ([], []),
    (["Charlie", "David"], [3, 4])
])
def test_lookup(used_names, input_lists, expected_ids):
    """Test if lookup returns the expected IDs."""
    assert expected_ids == used_names.lookup(input_lists)

@pytest.mark.parametrize("name_id, expected_string", [
    (0, "Alice"),
    (1, "Bob"),
    (2, "Eve"),
    (3, None)
])
def test_get__name_string(used_names, new_names, name_id, expected_string):
    """Test if get_name_string returns the expected string."""
    # Name is present
    assert used_names.get_name_string(name_id) == expected_string
    # Name is absent
    assert new_names.get_name_string(name_id) is None
