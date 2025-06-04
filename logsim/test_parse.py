"""Test the parse module.
"""

import pytest
import os
from scanner import Scanner
from parse import Parser
from names import Names
from devices import Devices
from monitors import Monitors
from network import Network

def generate_parser(path):
    names = Names()
    scanner = Scanner(path, names)
    #initiate objects
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    #create parser
    parser = Parser(names, devices, network, monitors, scanner)
    return names, devices, network, monitors, scanner, parser
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


#_dev tests
@pytest.mark.parametrize("device_type" ,[
    ("AND"),
    ("OR"),
    ("NAND"),
    ("NOR")
])
def test_dev_no_errors_16_input_gates(tmp_file, device_type):
    """Test that _dev() parses content correctly for 1 to 16 gates"""
    #Line to be checked
    content = f"A, B, C = {device_type}(16);"
    path = tmp_file(content)
    names, devices, network, monitors,scanner, parser = generate_parser(path)
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
    #Line to be checked
    content = "A, B, C = SWITCH(1);"
    path = tmp_file(content)
    names, devices, network, monitors,scanner, parser = generate_parser(path)
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
    #Line to be checked
    content = "A, B, C = CLOCK(100);"
    path = tmp_file(content)
    names, devices, network, monitors,scanner, parser = generate_parser(path)
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
    #Line to be checked
    content = "A, B, C = XOR;"
    path = tmp_file(content)
    names, devices, network, monitors,scanner, parser = generate_parser(path)
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
    #Line to be checked
    content = "A, B, C = DTYPE;"
    path = tmp_file(content)
    names, devices, network, monitors,scanner, parser = generate_parser(path)
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

@pytest.mark.parametrize("incorrect_content, error_msg",[
    (" .= XOR;", "device identifier expected"),
    ("A /= XOR;", "expected '='"),
    ("A = XBOR;", "invalid device type"),
    ("A, A = XOR;", "device identifier already used"),
    ("A = SWITCH(2)", "Expected binary input"),
    ("A = AND(a)", "pin number expected"),
    ("A = AND(18)", "pin number out of range (1-16)"),
    ("A = XOR(2)", "expected ';'")
])
def test_dev_correct_err_msg(tmp_file, capsys, incorrect_content, error_msg):
    """Assert incorrect statements produce correct error messages"""
    path = tmp_file(incorrect_content)
    names, devices, network, monitors,scanner, parser = generate_parser(path)
    #initialise symbol as done by parser parse_network method
    parser.symbol, parser.line, parser.column = parser.scanner.get_symbol(parser.line,parser.column)
    
    #initialise dev_list as done by parse_network
    parser.dev_list = []
    parser._dev()
    parser.stopping_set = [";"]
    parser._print_all_errors()
    assert parser.error_count == 1
    #error recovery to end of the line
    assert parser.symbol.type == scanner.EOF
    #relevant error message printed
    captout, capterrr = capsys.readouterr()
    assert error_msg in captout

def generate_parser_with_existing_devices(path):
    """Generate a parser with some existing devices for connections testing"""
    names = Names()
    scanner = Scanner(path, names)
    #initiate objects
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    #create parser
    parser = Parser(names, devices, network, monitors, scanner)
    name_str_list = ["A", "B", "C", "AND1", "XOR1", "D1"]
    name_ids = names.lookup(name_str_list)
    dev_kinds = [devices.SWITCH, devices.SWITCH, devices.CLOCK, devices.AND, devices.XOR, devices.D_TYPE]
    dev_params = [0,1,100,2,None,None]
    n_inputs = [None, None, None, 2, 2, 4]
    n_outputs = [1,1,1,1,1,2]
    #initialise symbol as done by parser parse_network method
    parser.symbol, parser.line, parser.column = parser.scanner.get_symbol(parser.line,parser.column)
    parser.dev_list = []
    for i in range(len(name_ids)):
        devices.make_device(name_ids[i], dev_kinds[i], dev_params[i])
        #The list is clearly redundant
        parser.dev_list.append(name_ids[i])
        parser.device_info[name_ids[i]] = (dev_kinds[i], n_inputs[i],n_outputs[i])
    return names, devices, network, monitors, scanner, parser

#_con tests
@pytest.mark.parametrize("correct_connection", [
    ("A -> AND1.I1;"),
    ("B -> AND1.I2;"),
    ("C -> D1.SET;"),
    ("D1.QBAR -> D1.CLK;"),
    ("D1.Q -> D1.DATA;"),
    ("C -> D1.CLEAR;")
])
def test_no_errors_con(tmp_file, correct_connection):
    """assert correct connection statements produce no errors 
    and that connections are made correctly"""
    path = tmp_file(correct_connection)
    names, devices, network, monitors,scanner, parser = generate_parser_with_existing_devices(path)
    parser.input_con_list = []
    parser._con()
    #NOTE - Dermot: i want to add another assertion to check that make_connection was
    # called correctly but not sure how
    assert parser.error_count == 0
    
    assert len(parser.input_con_list) == 1

@pytest.mark.parametrize("incorrect_content, error_msg",[
    (" -> B;", "device identifier expected"),
    ("A -> ;", "device identifier expected"),
    ("A.I1 -> B;", "invalid pin name"), #input to output
    ("A -> AND1.I3;", "expected I1..I2 on device AND1"),
    ("IDK -> A;", "device must be defined before use"),
    ("A -> XOR1.I14;", "XOR devices only support I1 and I2 (got I14) on XOR1"),
    ("A -> D1.I1;", "DTYPE input pin must be DATA, SET, CLEAR or CLK (got I) on D1"),
    ("C.Q -> AND1.I1;", "C does not have an output pin named Q"),
    ("A -> AND1.Iw;", "pin number expected"),
    ("A -> AND1.I1", "expected ';'"),
    ("AND1.I1 -> AND1.I1;", "invalid pin name"), #input to input, couldbe more descriptive
    ("D1.Q -> D1.Q", "invalid pin name"), #output to output
    ("A = B", "expected '->'")
])
def test_con_correct_err_msg(tmp_file, incorrect_content, error_msg, capsys):
    """Test _con prints correct error message for incorrect connection"""
    path = tmp_file(incorrect_content)
    names, devices, network, monitors,scanner, parser = generate_parser_with_existing_devices(path)
    parser.input_con_list = []
    parser.stopping_set = [";"]
    parser._con()
    parser._print_all_errors()
    assert parser.error_count == 1
    #relevant error message printed
    captout, capterrr = capsys.readouterr()
    assert error_msg in captout
    #error recovery to end of the line
    assert parser.symbol.type == scanner.EOF

def test_con_input_already_connected(tmp_file, capsys):
    """Test _con prints correct error message when you 
    try to connect 2 outputs to the same input"""
    path = tmp_file("A -> AND1.I1;")
    names, devices, network, monitors,scanner, parser = generate_parser_with_existing_devices(path)
    [dev_name] = names.lookup(["AND1"])
    parser.input_con_list = [(dev_name, "I1")]
    parser.stopping_set = [";"]
    parser._con()
    parser._print_all_errors()
    assert parser.error_count == 1
    assert parser.symbol.type == scanner.EOF
    captout, capterrr = capsys.readouterr()
    assert "input signal already connected, use an OR gate to combine signals" in captout

#_monitor
@pytest.mark.parametrize("output_names, output_pins", [
    (["A", "B", "D1", "AND1", "D1"], ["", "", ".Q", "", ".QBAR"]),
    (["A", "B", "C", "AND1", "XOR1"], ["","","","",""]),
    (["D1", "D1"], [".Q", ".QBAR"])
])
def test_monitor_correct_monitors(tmp_file, capsys, output_names, output_pins):
    """"Test that correct output signals are set to be monitored with no errors"""
    output_signals = [output_names[i]+output_pins[i] for i in range(len(output_names))]
    correct_monitor = "MONITOR{"+",".join(output_signals)+";}"
    print(correct_monitor)
    path = tmp_file(correct_monitor)
    names, devices, network, monitors,scanner, parser = generate_parser_with_existing_devices(path)
    parser.monitors_list = []
    parser._monitors()
    #No errors and every output is added to monitors_list
    assert parser.error_count == 0
    assert len(parser.monitors_list) == len(output_signals)
    output_ids = names.lookup(output_names)
    #check make_monitors has been called and signals added to monitored list
    monitored_list = monitors.get_signal_names()[0]
    for output_signal in output_signals:
        assert output_signal in monitored_list


@pytest.mark.parametrize("incorrect_monitor, error_msg", [
    (".", "expected MONITOR"),
    ("MONITOR.", "expected '{'"),
    ("MONITOR{.}", "device identifier expected"),
    ("MONITOR{ HELLO; }", "device must be defined before use"),
    ("MONITOR{A.BIG ;}", "invalid pin name"),
    ("MONITOR{A, WHAT;}", "device must be defined before use"),
    ("MONITOR{A, A;}", "signal already monitored"),
    ("MONITOR{A.Q;}", "A does not have an output pin named Q"),
    ("MONITOR{AND1.I1 }", "invalid pin name") #could be more descriptive
])
def test_monitor_correct_monitors(tmp_file, capsys, incorrect_monitor, error_msg):
    """"Test that correct error messages are produced for different errors"""
    path = tmp_file(incorrect_monitor)
    names, devices, network, monitors,scanner, parser = generate_parser_with_existing_devices(path)
    parser.monitors_list = []
    parser._monitors()
    parser._print_all_errors()
    assert parser.error_count == 1
    #Wasn't able to monitor signals so they aren't added to monitors_list
    assert len(parser.monitors_list) == 0
    #check make_monitors wasn't called
    monitored_list = monitors.get_signal_names()[0]
    assert len(monitored_list) == 0
    captout, capterr = capsys.readouterr()
    assert error_msg in captout












    



    
