"""Test the parse module.
It might be better to add a fixture for generating scanner, 
network, monitors, and parser from content
"""

import pytest
import os
from scanner import Scanner
from parse import Parser
from names import Names
from devices import Devices
from monitors import Monitors
from network import Network

#copied from test_scanner
@pytest.fixture
def tmp_file(tmp_path):
    """Return a filepath to a file containing the specified content"""
    def _create_file(content):
        """Helper to create a temporary file with given content"""
        file_path = tmp_path / "test.def"
        file_path.write_text(content)
        return str(file_path)
    return _create_file

@pytest.mark.parametrize("device_type" ,[
    ("AND"),
    ("OR"),
    ("NAND"),
    ("NOR")
])
def test_dev_no_errors_16_input_gates(tmp_file, device_type):
    """Test that _dev() parses content correctly for 1 to 16 gates"""
    names = Names()
    #Line to be checked
    content = f"A, B, C = {device_type}(16);"
    path = tmp_file(content)
    scanner = Scanner(path, names)
    #initiate objects
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    #create parser
    parser = Parser(names, devices, network, monitors, scanner)
    #initialise symbol as done by parser parse_network method
    parser.symbol, parser.line, parser.column = parser.scanner.get_symbol(parser.line,parser.column)
    #initialise dev_list as done by parse_network
    parser.dev_list = []

    parser._dev()
    assert parser.error_count == 0
    assert parser.symbol.type == scanner.EOF
    for nm in ["A", "B", "C"]:
        #assert every devce name has been added to the dev_list
        nm_id = names.query(nm)
        assert nm_id in parser.dev_list
        #check the device type was parsed correctly
        
        assert [devices.get_device(nm_id).device_kind] == names.lookup([device_type])
        #check the parameter was parsed correctly
        assert len(devices.get_device(nm_id).inputs) == 16

def test_no_dev_errors_switch(tmp_file):
    """Test that _dev parses content correctly for SWITCH statement"""
    names = Names()
    #Line to be checked
    content = "A, B, C = SWITCH(1);"
    path = tmp_file(content)
    scanner = Scanner(path, names)
    #initiate objects
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    #create parser
    parser = Parser(names, devices, network, monitors, scanner)
    #initialise symbol as done by parser parse_network method
    parser.symbol, parser.line, parser.column = parser.scanner.get_symbol(parser.line,parser.column)
    #initialise dev_list as done by parse_network
    parser.dev_list = []

    parser._dev()
    assert parser.error_count == 0
    assert parser.symbol.type == scanner.EOF
    for nm in ["A", "B", "C"]:
        #assert every devce name has been added to the dev_list
        nm_id = names.query(nm)
        assert nm_id in parser.dev_list
        #check the device type was parsed correctly
        
        assert devices.get_device(nm_id).device_kind == devices.SWITCH
        #check the parameter was parsed correctly
        assert devices.get_device(nm_id).switch_state == 1

def test_no_dev_errors_clock(tmp_file):
    """Test that _dev parses content correctly for CLOCK statement"""
    names = Names()
    #Line to be checked
    content = "A, B, C = CLOCK(100);"
    path = tmp_file(content)
    scanner = Scanner(path, names)
    #initiate objects
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    #create parser
    parser = Parser(names, devices, network, monitors, scanner)
    #initialise symbol as done by parser parse_network method
    parser.symbol, parser.line, parser.column = parser.scanner.get_symbol(parser.line,parser.column)
    #initialise dev_list as done by parse_network
    parser.dev_list = []

    parser._dev()
    assert parser.error_count == 0
    assert parser.symbol.type == scanner.EOF
    for nm in ["A", "B", "C"]:
        #assert every devce name has been added to the dev_list
        nm_id = names.query(nm)
        assert nm_id in parser.dev_list
        #check the device type was parsed correctly
        
        assert devices.get_device(nm_id).device_kind == devices.CLOCK
        #check the parameter was parsed correctly
        assert devices.get_device(nm_id).clock_half_period == 100

def test_no_dev_errors_xor(tmp_file):
    """Test that _dev parses content correctly for XOR statement"""
    names = Names()
    #Line to be checked
    content = "A, B, C = XOR;"
    path = tmp_file(content)
    scanner = Scanner(path, names)
    #initiate objects
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    #create parser
    parser = Parser(names, devices, network, monitors, scanner)
    #initialise symbol as done by parser parse_network method
    parser.symbol, parser.line, parser.column = parser.scanner.get_symbol(parser.line,parser.column)
    #initialise dev_list as done by parse_network
    parser.dev_list = []

    parser._dev()
    assert parser.error_count == 0
    assert parser.symbol.type == scanner.EOF
    for nm in ["A", "B", "C"]:
        #assert every devce name has been added to the dev_list
        nm_id = names.query(nm)
        assert nm_id in parser.dev_list
        #check the device type was parsed correctly
        
        assert devices.get_device(nm_id).device_kind == devices.XOR
        #check the parameter was parsed correctly
        assert len(devices.get_device(nm_id).inputs) == 2
        assert len(devices.get_device(nm_id).outputs) == 1

def test_no_dev_errors_dtype(tmp_file):
    """Test that _dev parses content correctly for DTYPE statement"""
    names = Names()
    #Line to be checked
    content = "A, B, C = DTYPE;"
    path = tmp_file(content)
    scanner = Scanner(path, names)
    #initiate objects
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    #create parser
    parser = Parser(names, devices, network, monitors, scanner)
    #initialise symbol as done by parser parse_network method
    parser.symbol, parser.line, parser.column = parser.scanner.get_symbol(parser.line,parser.column)
    #initialise dev_list as done by parse_network
    parser.dev_list = []

    parser._dev()
    assert parser.error_count == 0
    assert parser.symbol.type == scanner.EOF
    for nm in ["A", "B", "C"]:
        #assert every devce name has been added to the dev_list
        nm_id = names.query(nm)
        assert nm_id in parser.dev_list
        #check the device type was parsed correctly
        
        assert devices.get_device(nm_id).device_kind == devices.D_TYPE
        #check the parameter was parsed correctly
        assert len(devices.get_device(nm_id).inputs) == 4
        assert len(devices.get_device(nm_id).outputs) == 2
        #assert memory is not none
        assert devices.get_device(nm_id).dtype_memory in [0,1]
