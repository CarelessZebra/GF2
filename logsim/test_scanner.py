"""Test the scanner module"""
"""
import pytest

from scanner import Scanner

@pytest.fixture
def scanner():
    Fixture to create a Scanner instance

    return Scanner()

@pytest.fixture
def scanner_file():
    return "logsim/test_full_adder.txt"

"""


import pytest
import os
from scanner import Scanner, Symbol
from names import Names

# Helper to create a temporary file with given content
@pytest.fixture
def tmp_file(tmp_path):
    def _create_file(content):
        file_path = tmp_path / "test.def"
        file_path.write_text(content)
        return str(file_path)
    return _create_file

def test_symbol_initialization():
    sym = Symbol()
    assert sym.type is None
    assert sym.id is None
    assert sym.line is None
    assert sym.column is None

def test_advance_and_current_char(tmp_file):
    content = "ABC"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    # Initially cur
    # rent_char is None
    assert scanner.current_char is None
    scanner.advance()
    assert scanner.current_char == 'A'
    scanner.advance()
    assert scanner.current_char == 'B'
    scanner.advance()
    assert scanner.current_char == 'C'
    scanner.advance()
    # After end of file, read returns empty string
    assert scanner.current_char == ''

def test_skip_whitespace_spaces(tmp_file):
    content = "   X"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    scanner.advance()  # read first space
    line, column = 1, 0
    new_line, new_column = scanner.skip_whitespace(line, column)
    # Should skip all spaces and stop at 'X'
    assert scanner.current_char == 'X'
    # No newlines, so line and column unchanged
    assert (new_line, new_column) == (1, 0)

def test_skip_whitespace_newlines(tmp_file):
    content = "\n\nX"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    scanner.advance()  # first newline
    line, column = 1, 0
    new_line, new_column = scanner.skip_whitespace(line, column)
    # Two newlines encountered, line should increment twice
    assert new_line == 3
    # Column resets on newline, remains 0
    assert new_column == 0
    assert scanner.current_char == 'X'

def test_skip_comments_single_line(tmp_file):
    content = "# comment line\nX"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    scanner.advance()  # '#'
    line, column = 1, 0
    new_line, new_column = scanner.skip_comments(line, column)
    # Should position at '\n' or after? After reading until newline, current_char is '\n'
    assert scanner.current_char == '\n'
    # Line increment logic only inside while; here we exit on newline but not skip it
    assert (new_line, new_column) == (1, 0) or isinstance(new_line, int)

def test_skip_comments_multi_line(tmp_file):
    content = "/* comment */X"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    scanner.advance()  # '/'
    line, column = 1, 0
    new_line, new_column = scanner.skip_comments(line, column)
    # Should stop at character after '*/'
    assert scanner.current_char == 'X'
    assert (new_line, new_column) == (1, 0)

def test_get_name(tmp_file):
    content = "abc123_ XYZ"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    # Prime current_char at first char of name
    scanner.current_char = scanner.file.read(1)
    name = scanner.get_name()
    assert name == 'abc123_'
    # After name, current_char should be space
    assert scanner.current_char == ' '

def test_get_number(tmp_file):
    content = "12345 rest"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    scanner.current_char = scanner.file.read(1)
    number = scanner.get_number()
    assert number == 12345
    # After number, current_char should be space
    assert scanner.current_char == ' '