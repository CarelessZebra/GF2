"""Test the parse module"""

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
    """Test that _dev() parses content correctly for AND"""
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