"""Test the scanner module"""
import pytest

from scanner import Scanner

@pytest.fixture
def scanner():
    """Fixture to create a Scanner instance"""
    return Scanner()

