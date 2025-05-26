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

@pytest.mark.parametrize("num_error_codes, expected_codes", [
    (3, [0, 1, 2]),
    (5, [0, 1, 2, 3, 4]),
    (0, []),
    (-1, [])
])
def test_unique_error_codes(new_names, num_error_codes, expected_codes):
    """Test if unique_error_codes returns the expected list of error codes."""
    assert list(new_names.unique_error_codes(num_error_codes)) == expected_codes

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

@pytest.mark.parametrize("name_string, expected_id", [
    ("Alice", 0),
    ("Bob", 1),
    ("Eve", 2),
])
def test_query(used_names, new_names, name_string, expected_id):
    """Test if query returns the expected ID."""
    # Name is present
    assert used_names.query(name_string) == expected_id
    # Name is absent
    assert new_names.query(name_string) is None

#Test error codes for each function
def test_get_name_string_raises_exceptions(used_names):
    """Test if get_name_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.get_name_string(1.4)
    with pytest.raises(TypeError):
        used_names.get_name_string("hello")

def test_lookup_raises_exceptions(new_names):
    """Test if lookup raises expected exceptions."""
    with pytest.raises(TypeError):
        new_names.lookup(1.4)
    with pytest.raises(TypeError):
        new_names.lookup(5)
    with pytest.raises(TypeError):
        new_names.lookup([21])

def test_query_raises_exceptions(new_names):
    """Test if query raises expected exceptions."""
    with pytest.raises(TypeError):
        new_names.query(1.4)
    with pytest.raises(TypeError):
        new_names.query(5)
    with pytest.raises(ValueError):
        new_names.query("")

def test_unique_error_codes_raises_exceptions(new_names):
    """Test if unique_error_codes raises expected exceptions."""
    with pytest.raises(TypeError):
        new_names.unique_error_codes(1.4)
    with pytest.raises(TypeError):
        new_names.unique_error_codes("hello")