"""Test the scanner module"""
import pytest

from scanner import Scanner

@pytest.fixture
def scanner():
    """Fixture to create a Scanner instance"""
    return Scanner()

@pytest.fixture
def scanner_file():
    return "logsim/test_full_adder.txt"

@pytest.fixture
def scanner_with_file(scanner_file):
    """Fixture to create a Scanner instance with a file"""
    return Scanner(scanner_file)


