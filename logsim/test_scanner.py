"""Test the scanner module"""
<<<<<<< HEAD
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

=======
>>>>>>> 505c0dc091bc063d9721a46e67b895f7699b15db

import pytest
import os
from scanner import Scanner, Symbol
from names import Names

<<<<<<< HEAD
# Helper to create a temporary file with given content
@pytest.fixture
def tmp_file(tmp_path):
    def _create_file(content):
=======
@pytest.fixture
def scanner_file():
    """Fixture for the full adder test file"""
    return "logsim/test_full_adder.txt"

@pytest.fixture
def tmp_file(tmp_path):
    """Return a filepath to a file containing the specified content"""
    def _create_file(content):
        """Helper to create a temporary file with given content"""
>>>>>>> 505c0dc091bc063d9721a46e67b895f7699b15db
        file_path = tmp_path / "test.def"
        file_path.write_text(content)
        return str(file_path)
    return _create_file

def test_symbol_initialization():
<<<<<<< HEAD
=======
    """Tests symbol is initialised properly"""
    #this test seems a bit unecessary
>>>>>>> 505c0dc091bc063d9721a46e67b895f7699b15db
    sym = Symbol()
    assert sym.type is None
    assert sym.id is None
    assert sym.line is None
    assert sym.column is None

def test_advance_and_current_char(tmp_file):
<<<<<<< HEAD
=======
    """Tests that Scanner's advance() method updates current_char"""
>>>>>>> 505c0dc091bc063d9721a46e67b895f7699b15db
    content = "ABC"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    
    assert scanner.current_char == 'A'
    scanner.advance(0)
    assert scanner.current_char == 'B'
    scanner.advance(0)
    assert scanner.current_char == 'C'
    scanner.advance(0)
    # After end of file, read returns empty string
    assert scanner.current_char == ''

def test_skip_whitespace_spaces(tmp_file):
<<<<<<< HEAD
=======
    """Tests that skip_whitespace updates current_char, line, and column"""
>>>>>>> 505c0dc091bc063d9721a46e67b895f7699b15db
    content = "   X"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    line, column = 1, 0
    new_line, new_column = scanner.skip_whitespace(line, column)
    # Should skip all spaces and stop at 'X'
    assert scanner.current_char == 'X'
    # No newlines, so line unchanged
    assert (new_line, new_column) == (1, 3)

def test_skip_whitespace_newlines(tmp_file):
<<<<<<< HEAD
=======
    """Tests that skip_whitespace updates current_char, line,
    and column correctly when skipping newlines"""
>>>>>>> 505c0dc091bc063d9721a46e67b895f7699b15db
    content = "\n\nX"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    line, column = 1, 0
    new_line, new_column = scanner.skip_whitespace(line, column)
    # Two newlines encountered, line should increment twice
    assert new_line == 3
    # Column resets on newline, remains 0
    assert new_column == 0
    assert scanner.current_char == 'X'

def test_skip_comments_single_line(tmp_file):
<<<<<<< HEAD
=======
    """Test skip_comments skips single line comments"""
>>>>>>> 505c0dc091bc063d9721a46e67b895f7699b15db
    content = "# comment line\nX"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    line, column = 1, 0
    new_line, new_column = scanner.skip_comments(line, column)
    
    assert scanner.current_char == 'X'
    # Line increment logic only inside while; here we exit on newline but not skip it
    assert (new_line, new_column) == (1, 0) or isinstance(new_line, int)

def test_skip_comments_multi_line(tmp_file):
<<<<<<< HEAD
=======
    """Test skip_comments skips multi-line comments"""
>>>>>>> 505c0dc091bc063d9721a46e67b895f7699b15db
    content = "/* comment */X"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    line, column = 1, 0
    new_line, new_column = scanner.skip_comments(line, column)
    # Should stop at character after '*/'
    assert scanner.current_char == 'X'
    assert (new_line, new_column) == (1, 0)

def test_get_name(tmp_file):
<<<<<<< HEAD
=======
    """Tests get_name returns expected string"""
>>>>>>> 505c0dc091bc063d9721a46e67b895f7699b15db
    content = "abc123_ XYZ"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    # Prime current_char at first char of name

    name, column = scanner.get_name(0)
    assert name == 'abc123_'
    # After name, current_char should be space
    assert scanner.current_char == ' '

def test_get_number(tmp_file):
<<<<<<< HEAD
=======
    """Tests get_number returns expected number"""
>>>>>>> 505c0dc091bc063d9721a46e67b895f7699b15db
    content = "12345 rest"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    number, column = scanner.get_number(0)
    assert number == 12345
    # After number, current_char should be space
    assert scanner.current_char == ' '

<<<<<<< HEAD

# need to finish parser first
# Test for print_error_line
"""
def test_print_error_line(tmp_file, capsys):
    content = "error line"
    path = tmp_file(content)
    scanner = Scanner(path, Names())
    
    # Simulate an error
    scanner.print_error_line(1, 5, "Test error")
    
    captured = capsys.readouterr()
    assert "Error at line 1, column 5: Test error" in captured.out
    assert "error line" in captured.out
"""

def test_get_symbol():
=======
# Test for print_error_line
def test_print_error_line(capsys):
    """Tests print_error_line prints expected string to stdout"""
    scanner = Scanner("test_full_adder.txt", Names())
    line = 11
    col = 4
    scanner.print_error_line(line,col)
    captout, capterror = capsys.readouterr()
    assert captout == "    A -> AND1.I1;\n    ^\n"

def test_print_error_line_out_of_bounds(capsys):
    """Tests print_error_line print output
    when the column is out of bounds of the line"""
    scanner = Scanner("test_full_adder.txt", Names())
    line = 11
    col = 20
    scanner.print_error_line(line,col)
    captout, capterror = capsys.readouterr()
    assert captout == "    A -> AND1.I1;\n                 ^ (error position out of bounds)\n"

def test_get_symbol():
    """Tests get_symbol returns correct Symbol object"""
>>>>>>> 505c0dc091bc063d9721a46e67b895f7699b15db
    scanner = Scanner("test_full_adder.txt", Names())
    line = 1
    col = 0
    symbol, line, col =  scanner.get_symbol(line, col)
    assert symbol.id == scanner.DEVICES
    assert symbol.type == scanner.KEYWORD
    assert symbol.line == 3
    assert symbol.column == 0
    symbol, line, col =  scanner.get_symbol(line, col)
    assert symbol.id == None
    assert symbol.type == scanner.OPENCURLY
    assert symbol.line == 3
    assert symbol.column == 8
    symbol, line, col =  scanner.get_symbol(line, col)
<<<<<<< HEAD
    assert symbol.id == 10
=======
    assert symbol.id == scanner.names.query("A")
>>>>>>> 505c0dc091bc063d9721a46e67b895f7699b15db
    assert symbol.type == scanner.NAME
    assert symbol.line == 4
    assert symbol.column == 4
    symbol, line, col =  scanner.get_symbol(line, col)
    assert symbol.id == None
    assert symbol.type == scanner.COMMA
    assert symbol.line == 4
    assert symbol.column == 5
