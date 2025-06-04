"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""
from __future__ import annotations
from typing import Optional, List, Tuple

#from scanner import Scanner
class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise attributes."""
        self.scanner = scanner
        self.names = names
        self.devices = devices
        self.network = network  
        self.monitors = monitors
        self.symbol = (None)
        self.error_count = 0
        self.line = 1
        self.column = 0
        self.stopping_set = []
        self.error_flag = False #This means a syntax block can terminate early if an error is flagged
        self.errors = [] #keep track of error codes, line, and col for printing
        self.device_info: dict[int, Tuple[int,int,int]] = {}

    def _advance(self):
        """Fetch the next symbol from the scanner, updating line/column."""
        self.symbol, self.line, self.column = self.scanner.get_symbol(
            self.line, self.column
        )

    # -----------------------------------------------------------------------
    def _accept(self, sym_type: int, sym_id: Optional[int] = None) -> bool:
        """If the *current* symbol matches the requested type (and optional ID)
        consume it and return **True**;
        otherwise leave it in place and return **False**."""
        if self.symbol.type == sym_type and (sym_id is None or self.symbol.id == sym_id):
            self._advance()
            return True
        return False

    # -----------------------------------------------------------------------
    def _expect(self, sym_type: int, sym_id: Optional[int] = None):
        """Like :meth:`_accept` but emits an error (with recovery) when the
        symbol does not match."""
        if not self._accept(sym_type, sym_id):
            self._error(f"expected {self._tok_desc(sym_type, sym_id)}")

        # -----------------------------------------------------------------------
    def _error(self, error_msg):
        self.error_count += 1
        self.error_flag = True
        # This is a very scuffed way of not printing error messages if we have already reached EOF
        self.errors.append((error_msg, self.symbol.line, self.symbol.column))
        #NOTE - The commented out bit doesn't solve the root cause which is that the parser
        #should stop parsing if it gets to EOF, so recursive returns need to be improved.
        #if self.symbol.type!=self.scanner.EOF:
            #self.errors.append((error_msg, self.symbol.line, self.symbol.column))
            #print(f"Parser error (line {self.symbol.line}, col {self.symbol.column}): {message}")
        #else:
        #    return
        while (self.symbol.type not in self.stopping_set and
                self.symbol.type != self.scanner.EOF):
            self._advance()
        if self.symbol.type == self.scanner.EOF:
            #This is for debugging
            #print("Error recovery was not possible, end of file reached")
            pass
        else:
            self._advance()

    def _print_all_errors(self):
        for error_msg, line, column in self.errors:
            self.scanner.print_error_line(line, column)
            print(error_msg)

    def _tok_desc(self, t: int, i: Optional[int]) -> str:
        """Return a short, human‑readable description of the token *t/i*."""
        if t == self.scanner.KEYWORD or t == self.scanner.NAME:
            return self.names.get_name_string(i)
        mapping = {
            self.scanner.SEMICOLON:       "';'",
            self.scanner.COMMA:           "','",
            self.scanner.EQUALS:          "'='",
            self.scanner.ARROW:           "'->'",
            self.scanner.FULLSTOP:        "'.'",
            self.scanner.OPENCURLY:       "'{'",
            self.scanner.CLOSECURLY:      "'}'",
            self.scanner.OPENBRAC:       "'('",
            self.scanner.CLOSEBRAC:      "')'",
        }
        return mapping.get(t, f"token_type_{t}")
    
    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        self.symbol, self.line, self.column = self.scanner.get_symbol(self.line,self.column)

        #device list
        self.dev_list: List[int] = []
        self.input_con_list: List[Tuple[int, Optional[int]]] = []  # list of connections
        self.monitors_list: List[Tuple[int, Optional[int]]] = []  # list of monitors 

        guitest = False
        if guitest:
            return True
        else:
            self._spec()
            self._print_all_errors()
            if self.error_count == 0:
                return True
            return False

    def _is_kw(self, kw_id: int) -> bool:
        return self.symbol.type == self.scanner.KEYWORD and self.symbol.id == kw_id
    
    #  EBNF   spec        = devices, connections, monitors ;
    def _spec(self):
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.DEVICES:
            self._devices()
        else:
            self._error("Expected DEVICES block")
            return
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.CONNECTIONS:
            self._connections()
        else:
            self._error("Expected CONNECTIONS block")
            return
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.MONITOR:
            self._monitors()
        else:
            self._error("Expected MONITORS block")
            return

    #  devices = "DEVICES" "{" dev { dev } "}" ;
    def _devices(self):
        self._expect(self.scanner.KEYWORD, self.scanner.DEVICES)
        if self.error_flag:
            self.error_flag = False
            return False
        self._expect(self.scanner.OPENCURLY)
        if self.error_flag:
            self.error_flag = False
            return False
        self.stopping_set = [self.scanner.CLOSECURLY, self.scanner.SEMICOLON]
        self._dev()
        
        while self.symbol.type != self.scanner.CLOSECURLY:
            if self.symbol.type == self.scanner.NAME:
                self._dev()
            else:
                self._error("device identifier expected")
                return False

        self.stopping_set = [self.scanner.CLOSECURLY]
        self._expect(self.scanner.CLOSECURLY)
        if self.error_flag:
            self.error_flag = False
            return False
        self.stopping_set = []

    #  dev = device_name { "," device_name } '=' device_type ';' ;


    def _dev(self):
        #if an error flag is raised then need to not run the rest
        name_id = self.symbol.id  # remember the device name

        if name_id in self.dev_list:
            self._error("device identifier already used")
            #print([self.names.get_name_string(i) for i in self.dev_list])
            self.error_flag = False
            return False

        names_list: List[int] = [self._device_name()]  # first identifier consumed

        if self.error_flag:
            self.error_flag = False
            return False

        while self._accept(self.scanner.COMMA):

            name_id = self.symbol.id  # remember the device name
            if name_id in names_list:
                self._error("device identifier already used")
                #print([self.names.get_name_string(i) for i in self.dev_list])
                self.error_flag = False
                return False


            names_list.append(self._device_name())

            if self.error_flag:
                self.error_flag = False
                return False



        self._expect(self.scanner.EQUALS)

        if self.error_flag:
            self.error_flag = False
            return False

        try: 
            dev_kind, param = self._device_type()
        except:
            dev_kind, param = None, None
        if (dev_kind, param) == (None, None):
            return False

        self._expect(self.scanner.SEMICOLON)

        if self.error_flag:
            self.error_flag = False
            return False
        
    
        # ── semantic action here (e.g. create device(s))
        # for nm in names:
        #     self.devices.make_device(nm, dev_kind, param)
        #return True
        for nm in names_list:
            self.dev_list.append(nm)  # add to device list if no errors occur
            if dev_kind in (
                self.devices.AND,
                self.devices.NAND,
                self.devices.OR,
                self.devices.NOR,
            ):
               # param is the number of inputs (from AND(N), etc.), 1 output
                n_inputs = param
                n_outputs = 1

            elif dev_kind == self.devices.XOR:
                # XOR devices always have exactly 2 inputs by spec, 1 output
                n_inputs = 2
                n_outputs = 1

            elif dev_kind == self.devices.D_TYPE:
                # D-flip-flop: 4 named inputs (DATA, SET, CLR, CLK), 2 outputs (Q, QBAR)
                n_inputs = 4
                n_outputs = 2

            elif dev_kind == self.devices.SWITCH:
                n_inputs  = 0
                n_outputs = 1

            elif dev_kind == self.devices.CLOCK:
                n_inputs  = 0
                n_outputs = 1

            else:
                # (If you add more device types in future, handle here)
                n_inputs  = 0
                n_outputs = 1

            self.device_info[nm] = (dev_kind, n_inputs, n_outputs)
            error = self.devices.make_device(nm, dev_kind, param)
            if error != self.devices.NO_ERROR:
                print("make_device error", error)

        return True
    
    #  device_type = gate | switch | clock | "DTYPE" | "XOR" ;
    def _device_type(self) -> Tuple[Optional[int], Optional[int]]:
        if self._is_kw(self.scanner.AND) or self._is_kw(self.scanner.NAND) or self._is_kw(self.scanner.NOR) or self._is_kw(self.scanner.OR):
            return self._gate()
        elif self._is_kw(self.scanner.SWITCH):
            return self._switch()
        elif self._is_kw(self.scanner.CLOCK):
            return self._clock()
        elif self._accept(self.scanner.KEYWORD, self.scanner.DTYPE):
            return (self.devices.D_TYPE, None)
        elif self._accept(self.scanner.KEYWORD, self.scanner.XOR):
            return (self.devices.XOR, None)
        else:
            self._error("invalid device type")
            return (None, None)

    #  gate = ( "AND" | "NAND" | "NOR" | "OR" ) '(' pin_number ')' ;
    def _gate(self):
        # BUG - devices doesn't have a GATE attribute
        gate_kw = self.symbol.id  # remember which gate
        self._advance()
        self._expect(self.scanner.OPENBRAC)
        
        if self.error_flag:
            self.error_flag = False
            return False
        
        pins = self._pin_number()
        
        if self.error_flag:
            self.error_flag = False
            return False
        
        self._expect(self.scanner.CLOSEBRAC)
        
        if self.error_flag:
            self.error_flag = False
            return False
        
        return (gate_kw, pins)

    #  switch = "SWTICH", "(", binary, ")" ;   binary = '0' | '1';
    def _switch(self):
        self._expect(self.scanner.KEYWORD, self.scanner.SWITCH)

        if self.error_flag:
            self.error_flag = False
            return False
        
        self._expect(self.scanner.OPENBRAC)

        if self.error_flag:
            self.error_flag = False
            return False
        
        value = self.symbol.id  # 0 or 1
        if value not in [0, 1]:
            self._error("Expected binary input")

        if self.error_flag:
            self.error_flag = False
            return False
        
        self._advance()
        self._expect(self.scanner.CLOSEBRAC)

        if self.error_flag:
            self.error_flag = False
            return False
        
        return (self.devices.SWITCH, value)

    #  clock = "CLOCK" '(' integer ')' ;
    def _clock(self):
        self._expect(self.scanner.KEYWORD, self.scanner.CLOCK)
        if self.error_flag:
            self.error_flag = False
            return False
        self._expect(self.scanner.OPENBRAC)
        if self.error_flag:
            self.error_flag = False
            return False
        period = self._integer()
        if self.error_flag:
            self.error_flag = False
            return False
        self._expect(self.scanner.CLOSEBRAC)
        if self.error_flag:
            self.error_flag = False
            return False
        return (self.devices.CLOCK, period)

    # ─────────────────────────────────────────────────────── CONNECTIONS block
    #  connections = "CONNECTIONS" '{' con { con } '}' ;
    def _connections(self):
        self._expect(self.scanner.KEYWORD, self.scanner.CONNECTIONS)

        if self.error_flag:
            self.error_flag = False
            return False
        self._expect(self.scanner.OPENCURLY)

        if self.error_flag:
            self.error_flag = False
            return False
        
        self.stopping_set = [self.scanner.CLOSECURLY, self.scanner.SEMICOLON]

        if self.error_flag:
            self.error_flag = False
            return False
        
        self._con()

        while self.symbol.type == self.scanner.NAME:
            self._con()
            
        self.stopping_set = [self.scanner.CLOSECURLY]
        self._expect(self.scanner.CLOSECURLY)
        if self.error_flag:
            self.error_flag = False
            return False
        self.stopping_set = []

    #  con = signal '->' signal ';' ;
    def _con(self):
        """Syntax/semantic checks for each connection statement"""
        output_signal = self._output_signal()

        if not output_signal:
            return False
        
        self._expect(self.scanner.ARROW)
        if self.error_flag:
            self.error_flag = False
            return False
        input_signal = self._input_signal()
        if not input_signal:
            return False
        if input_signal in self.input_con_list:
            self._error("input signal already connected, use an OR gate to combine signals")
            self.error_flag = False
            return False
        
        self.input_con_list.append(input_signal)  # add output device to input signal


        self._expect(self.scanner.SEMICOLON)

        if self.error_flag:
            self.error_flag = False
            return False
        # ── semantic action here (e.g. connect signals)
        if self.error_count==0:
            in_dev_id, in_pin = input_signal
            in_pin = self.names.query(in_pin)
            # Adi I don't know what your extra variable is
            out_dev_id, (out_pin, some_variable) = output_signal
            out_pin = self.names.query(out_pin)
            
            if out_pin != self.names.query("O"):
                error = self.network.make_connection(out_dev_id, out_pin, in_dev_id, in_pin)
            else:
                error = self.network.make_connection(out_dev_id, None,in_dev_id, in_pin)
            if error!=self.network.NO_ERROR:
                #print(self.devices.get_device(out_dev_id).device_kind, out_pin)
                #print(self.devices.get_device(in_dev_id).device_kind, in_pin)
                print("Make_connections error:", error)


    #  input_signal = device_name, ".", input_pin_name;
    def _input_signal(self):
        dev = self.symbol.id
        if dev not in self.dev_list and self.symbol.type == self.scanner.NAME:
            self._error("device must be defined before use")
            #print([self.names.get_name_string(i) for i in self.dev_list])
            self.error_flag = False
            return False
        dev = self._device_name()
        if self.error_flag:
            self.error_flag = False
            return False
        kind, n_in, n_out = self.device_info.get(dev, (None, 0, 0))

        if self.error_flag:
            self.error_flag = False
            return False
        self._expect(self.scanner.FULLSTOP)
        if self.error_flag:
            self.error_flag = False
            return False
        pin = self._input_pin_name()
        
        if self.error_flag:
            self.error_flag = False
            return False
        
        pin_label, pin_index = pin
        pin_name = "".join([pin_label, str(pin_index)])

        if kind in (
            self.devices.AND,
            self.devices.NAND,
            self.devices.OR,
            self.devices.NOR,
        ):
            # 1-to-N gate: must use I1..I{n_in}
            if pin_label != "I" or not (1 <= pin_index <= n_in):
                self._error(f"expected I1..I{n_in} on device {self.names.get_name_string(dev)}")
                self.error_flag = False
                return False
            

        elif kind == self.devices.XOR:
            # XOR only permits I1 or I2
            if pin_label != "I" or pin_index not in (1, 2):
                self._error(f"XOR devices only support I1 and I2 (got {pin_label}{pin_index}) on {self.names.get_name_string(dev)}")
                self.error_flag = False
                return False

        elif kind == self.devices.D_TYPE:
            # DTYPE’s inputs must be DATA / SET / CLEAR / CLK
            if pin_label not in ("DATA", "SET", "CLEAR", "CLK"):
                self._error(f"DTYPE input pin must be DATA, SET, CLEAR or CLK (got {pin_label}) on {self.names.get_name_string(dev)}")
                self.error_flag = False
                return False
            return (dev, pin_label)
            
        else:
            # SWITCH & CLOCK have no named input pins
            self._error(f"device {self.names.get_name_string(dev)} has no input pins")
            self.error_flag = False
            return False

        return (dev, pin_name)


    # output_signal = device_name, [".", output_pin_name];

    def _output_signal(self):
        """Checks output signal syntax output_signal = device_name, [".", output_pin_name];"""
        dev = self.symbol.id
        if dev not in self.dev_list and self.symbol.type == self.scanner.NAME:
            self._error("device must be defined before use")
            self.error_flag = False
            return False
        dev = self._device_name()
        if self.error_flag:
            self.error_flag = False
            return False

        # Look up (kind, n_in, n_out) for this device
        kind, _, n_out = self.device_info.get(dev, (None, 0, 0))

        # If the user wrote “.something”
        if self._accept(self.scanner.FULLSTOP):
            output_pin_name = self._output_pin_name()
            if self.error_flag:
                self.error_flag = False
                return False#
            pin_label, _ = output_pin_name

            # ── ADDED semantic check: only DTYPE can use Q/QBAR
            if kind == self.devices.D_TYPE:
                if pin_label not in ("Q", "QBAR"):
                    self._error(
                        f"DTYPE output pin must be Q or QBAR "
                        f"(got {pin_label}) on {self.names.get_name_string(dev)}"
                    )
                    self.error_flag = False
                    return False
            else:
                # any other device has exactly one unnamed output, so “.Q” is illegal
                self._error(
                    f"{self.names.get_name_string(dev)} "
                    f"does not have an output pin named {pin_label}"
                )
                self.error_flag = False
                return False

            return (dev, (pin_label, None))

        # No “.pin” was written: allowed only if exactly one output exists
        if n_out == 0:
            self._error(
                f"{self.names.get_name_string(dev)} has no outputs. This could be due to a prior issue e.g. repeated device name."
            )
            self.error_flag = False
            return False
        if n_out != 1:
            self._error(
                f"{self.names.get_name_string(dev)} requires an explicit "
                "output pin name (Q or QBAR)."
            )
            self.error_flag = False
            return False

        # Implicit single output:
        return (dev, ("O", None))

    # ───────────────────────────────────────────────────────── MONITOR block
    #  monitors = "MONITOR" '{' signal { ',' signal } ';' '}' ;
    def _monitors(self):
        """Checks monitors syntax and makes monitor for each signal"""
        self._expect(self.scanner.KEYWORD, self.scanner.MONITOR)

        if self.error_flag:
            self.error_flag = False
            return False
        
        self._expect(self.scanner.OPENCURLY)

        if self.error_flag:
            self.error_flag = False
            return False
        
        self.stopping_set = [self.scanner.CLOSECURLY, self.scanner.SEMICOLON]
        output_signal = self._output_signal()
    
        if not output_signal:
            return False
        
        if output_signal in self.monitors_list:
            self._error("signal already monitored")
            self.error_flag = False
            return False
        
        local_monitors = [output_signal]

        while self._accept(self.scanner.COMMA):
            if self.symbol.type != self.scanner.CLOSECURLY:
                output_signal = self._output_signal()
            if not output_signal:
                return False
            if output_signal in local_monitors:
                self._error("signal already monitored")
                self.error_flag = False
                return False            
            
            local_monitors.append(output_signal)  # add output signal to monitor list

        self.stopping_set = [self.scanner.CLOSECURLY]
        self._expect(self.scanner.SEMICOLON)
        if self.error_flag:
            self.error_flag = False
            return False
        self._expect(self.scanner.CLOSECURLY)
        if self.error_flag:
            self.error_flag = False
            return False
        self.stopping_set = []

        #call make monitors
        for output_signal in local_monitors:
            self.monitors_list.append(output_signal)
            # Adi I don't know what your extra variable is
            out_dev_id, (out_pin, some_variable) = output_signal
            out_pin = self.names.query(out_pin)
            error = self.monitors.make_monitor(out_dev_id, out_pin)
            if error != self.monitors.NO_ERROR:
                print("make_monitor error", error)
            

    # ──────────────────────────────────────────────────────────── primitives
    # input_pin_name = 'DATA' | 'SET' | 'CLR' | 'CLK' | 'I' pin_number ;
    def _input_pin_name(self):
        """Checks input pin name is in 'DATA' | 'SET' | 'CLR' | 'CLK' | 'I' pin_number """
        if self.symbol.type in [self.scanner.NAME, self.scanner.KEYWORD]:
            text = self.names.get_name_string(self.symbol.id).upper()
            if text[0] == 'I':
                # NOTE - This might be possible to do using pin number but
                # it is easier to do like this as I16 is read as one symbol here
                # whilst in AND(16), 16 is the symbol
                num = text[1:]
                if not num.isdigit():
                    self._error("pin number expected")
                    return (None, None)
                num = int(num)
                if not (1 <= num <= 16):
                    self._error("pin number out of range (1-16)")
                    return (None, None)
                self._advance()
                return ('I', num)
            elif text in ('DATA', 'SET', 'CLEAR', 'CLK'):
                self._advance()
                return (text, None)
        self._error("invalid pin name")
        return None

    # output_pin_name = 'Q' | 'QBAR';
    def _output_pin_name(self):
        """checks output pin name is Q or QBAR"""
        if self.symbol.type in (self.scanner.NAME, self.scanner.KEYWORD):
            text = self.names.get_name_string(self.symbol.id).upper()
            if text in ('Q', 'QBAR'):
                self._advance()
                return (text, None)
        self._error("invalid pin name")
        return None

    #  pin_number 1–16 (inclusive)
    def _pin_number(self):
        """Checks pin number is between 1 and 16 """
        if self.symbol.type != self.scanner.NUMBER:
            self._error("pin number expected")
            return None
        value = self.symbol.id
        if not (1 <= value <= 16):
            self._error("pin number out of range (1-16)")
        self._advance()
        return value

    #  integer = non‑empty sequence of digits (scanner already returns NUMBER)
    def _integer(self):
        """Checks integer = non‑empty sequence of digits (scanner already returns NUMBER)"""
        if self.symbol.type != self.scanner.NUMBER:
            self._error("integer expected")
            return 0
        value = self.symbol.id
        self._advance()
        return value

    #  device_name = NAME token
    def _device_name(self):
        """Checks device_name = NAME token"""
        if self.symbol.type != self.scanner.NAME:
            self._error("device identifier expected")
            return None
        name_id = self.symbol.id
        self._advance()
        return name_id

