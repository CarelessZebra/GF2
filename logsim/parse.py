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
        # syntax block can terminate early if an error is flagged
        self.error_flag = False
        # keep track of error codes, line, and col for printing
        self.errors = []
        self.device_info: dict[int, Tuple[int, int, int]] = {}
        self.end_of_block = False

    def _advance(self):
        """Fetch the next symbol from the scanner, updating line/column."""
        self.symbol, self.line, self.column = self.scanner.get_symbol(
            self.line, self.column
        )

    # -----------------------------------------------------------------------
    def _accept(self, sym_type: int, sym_id: Optional[int] = None) -> bool:
        """
        Return true if the next symbol matches or False if it doesn't.

        If the *current* symbol matches the requested type and optional ID
        consume it and return **True**;
        otherwise leave it in place and return **False**.
        """
        if self.symbol.type == sym_type and (sym_id is None or self.symbol.id == sym_id):
            self._advance()
            return True
        return False

    # -----------------------------------------------------------------------
    def _expect(self, sym_type: int, sym_id: Optional[int] = None):
        """Like :meth:`_accept` but emits an error when the symbol is wrong."""
        if not self._accept(sym_type, sym_id):
            self._error(f"expected {self._tok_desc(sym_type, sym_id)}   on line {self.line}")

        # -----------------------------------------------------------------------
    def _error(self, error_msg):
        self.error_count += 1
        self.error_flag = True
        self.errors.append((error_msg, self.symbol.line, self.symbol.column))
        # advance until stopping symbol is found
        while (self.symbol.type not in self.stopping_set and
                self.symbol.type != self.scanner.EOF):
            self._advance()
        if self.symbol.type == self.scanner.EOF:
            # This is for debugging
            # print("Error recovery was not possible, end of file reached")
            pass
        elif self.symbol.type == self.scanner.CLOSECURLY and self.scanner.CLOSECURLY in self.stopping_set:
            # don't advance if we encounter a closecurly
            # this is so parsing can resume without error
            pass
        else:
            self._advance()

    def _print_all_errors(self):
        if self.scanner.comment_opened:
            self.errors.insert(0,("Unclosed comment", self.scanner.comment_opened_line, self.scanner.comment_opened_column))
        for error_msg, line, column in self.errors:
            self.scanner.print_error_line(line, column)
            print(f"{error_msg} on line {line}")

        print(f"\nTotal errors: {self.error_count}")

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
        self.symbol, self.line, self.column = self.scanner.get_symbol(self.line, self.column)

        # device list
        self.dev_list: List[int] = []
        # list of connections
        self.input_con_list: List[Tuple[int, Optional[int]]] = []
        # list of monitors
        self.monitors_list: List[Tuple[int, Optional[int]]] = []

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
            self._error("Expected MONITOR block")
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
        
        #print(self.error_count)
        self._dev()
        #print(self.error_count)
        #print(self.symbol.type==self.scanner.NAME)

        while self.symbol.type != self.scanner.CLOSECURLY:
            if self.symbol.type == self.scanner.NAME:
                #print("hello", self.symbol.line, self.symbol.column)
                #print(self.error_count)
                #print("do you accept comma here")
                #print(self.names.get_name_string(self.symbol.id))
                self._dev()
                #print(self.error_count)
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
        """Check dev syntax."""
        # if an error flag is raised then need to not run the rest
        name_id = self.symbol.id  # remember the device name
        #print(self.names.get_name_string(name_id))
        if name_id in self.dev_list:
            self._error("device identifier already used")
            # print([self.names.get_name_string(i) for i in self.dev_list])
            self.error_flag = False
            return False
        # first identifier added to names list
        #print("hello", self.names.get_name_string(self.symbol.id))
        names_list: List[int] = [self._device_name()]

        if self.error_flag:
            print("error")
            self.error_flag = False
            return False
        #print("dev comma:")
        #print(self.symbol.type==self.scanner.COMMA, self.symbol.line)
        while self._accept(self.scanner.COMMA):
            #print("accepts comma")
            name_id = self.symbol.id  # remember the device name
            if name_id in names_list:
                self._error("device identifier already used")
                # print([self.names.get_name_string(i) for i in self.dev_list])
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
        except Exception:
            dev_kind, param = None, None
        if (dev_kind, param) == (None, None):
            #print("returns here")
            #print(self.symbol.type==self.scanner.NAME, self.symbol.line)
            # NOTE NOTE NOTE DON'T REMOVE THIS FLAG THE ENTIRE 
            # CODEBASE DEPENDS ON IT NOTE NOTE NOTE
            self.error_flag = False
            return False

        self._expect(self.scanner.SEMICOLON)

        if self.error_flag:
            self.error_flag = False
            return False

        # ── semantic action here (e.g. create device(s))
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
                # D-flip-flop: 4 named inputs (DATA, SET, CLR, CLK)
                # 2 outputs (Q, QBAR)
                n_inputs = 4
                n_outputs = 2

            elif dev_kind == self.devices.SWITCH:
                n_inputs = 0
                n_outputs = 1

            elif dev_kind == self.devices.CLOCK:
                n_inputs = 0
                n_outputs = 1

            elif dev_kind == self.devices.SIGGEN:
                # Signal generator: 0 inputs, 1 output
                n_inputs = 0
                n_outputs = 1

            else:
                # (If you add more device types in future, handle here)
                n_inputs = 0
                n_outputs = 1

            self.device_info[nm] = (dev_kind, n_inputs, n_outputs)
            error = self.devices.make_device(nm, dev_kind, param)
            if error != self.devices.NO_ERROR:
                print("make_device error", error)

        return True

    #  device_type = gate | switch | clock | "DTYPE" | "XOR" ;
    def _device_type(self) -> Tuple[Optional[int], Optional[int]]:
        """Call correct device syntax checking function."""
        if self._is_kw(self.scanner.AND) or self._is_kw(self.scanner.NAND) or self._is_kw(self.scanner.NOR) or self._is_kw(self.scanner.OR):
            return self._gate()
        elif self._is_kw(self.scanner.SWITCH):
            return self._switch()
        elif self._is_kw(self.scanner.CLOCK):
            return self._clock()
        


        elif self._is_kw(self.scanner.SIGGEN):
            return self._siggen()
        elif self._accept(self.scanner.KEYWORD, self.scanner.DTYPE):
            return (self.devices.D_TYPE, None)
        elif self._accept(self.scanner.KEYWORD, self.scanner.XOR):
            return (self.devices.XOR, None)
        else:
            self._error("invalid device type")
            return (None, None)

    #  gate = ( "AND" | "NAND" | "NOR" | "OR" ) '(' pin_number ')' ;
    def _gate(self):
        """Check gate syntax for 1-16 input gates."""
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
        """Check switch syntax."""
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
        """Check clock syntax."""
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
    
    #  siggen = "SIGGEN" '(' binary {',' binary} ')' ;

    def _siggen(self):
        """Check signal generator syntax."""
        #print("enter in siggen")
        self._expect(self.scanner.KEYWORD, self.scanner.SIGGEN)
        #print("siggen keyword accepted")
        if self.error_flag:
            self.error_flag = False
            return False
        
        self._expect(self.scanner.OPENBRAC)
        #print("siggen openbrac accepted")
        if self.error_flag:
            self.error_flag = False
            return False
        
        if self.symbol.id not in [0, 1]:
            #print("first siggen symbol id not in [0, 1]")
            self._error("Expected binary input in SIGGEN LIST")

        if self.error_flag:   
            self.error_flag = False
            return False


        pattern = [self.symbol.id]  # start with first binary value
        #print(f"pattern curerntly {pattern}")
        self._advance()  # move to next symbol
        
        while self.symbol.type == self.scanner.COMMA:
            #print("siggen comma accepted")
            self._advance()  # move to next symbol after comma
            if self.symbol.id not in [0, 1]:
                self._error("Expected binary input in SIGGEN LIST")
                self.error_flag = False
                return False
            pattern.append(self.symbol.id) # add binary value to pattern
            print(f"pattern currently {pattern}")
            self._advance()  # move to next symbol after binary value

        self._expect(self.scanner.CLOSEBRAC)

        if self.error_flag:
            self.error_flag = False
            return False

        return (self.devices.SIGGEN, pattern)  


    # ─────────────────────────────────────────────────────── CONNECTIONS block
    #  connections = "CONNECTIONS" '{' con { con } '}' ;
    def _connections(self):
        """Check connections syntax."""
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
        """Syntax/semantic checks for each connection statement."""
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

        # add output device to input signal
        self.input_con_list.append(input_signal)

        self._expect(self.scanner.SEMICOLON)

        if self.error_flag:
            self.error_flag = False
            return False
        # ── semantic action here (e.g. connect signals)
        if self.error_count == 0:
            in_dev_id, in_pin = input_signal
            in_pin = self.names.query(in_pin)
            # Adi I don't know what your extra variable is
            out_dev_id, (out_pin, some_variable) = output_signal
            out_pin = self.names.query(out_pin)

            if out_pin != self.names.query("O"):
                error = self.network.make_connection(out_dev_id, out_pin, in_dev_id, in_pin)
            else:
                error = self.network.make_connection(out_dev_id, None, in_dev_id, in_pin)
            if error != self.network.NO_ERROR:
                # print(self.devices.get_device(out_dev_id).device_kind, out_pin)
                # print(self.devices.get_device(in_dev_id).device_kind, in_pin)
                print("Make_connections error:", error)

    # input_signal = device_name, ".", input_pin_name;
    def _input_signal(self):
        """Check input signal syntax."""
        dev = self.symbol.id
        if dev not in self.dev_list and self.symbol.type == self.scanner.NAME:
            self._error("device must be defined before use")
            # print([self.names.get_name_string(i) for i in self.dev_list])
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
        """
        Check output signal syntax.

        output_signal = device_name, [".", output_pin_name];.
        """
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
                return False
            pin_label, _ = output_pin_name

            # ── ADDED semantic check: only DTYPE can use Q/QBAR
            if kind == self.devices.D_TYPE:
                if pin_label not in ("Q", "QBAR"):
                    self._error(
                        f"DTYPE output pin must be Q or QBAR " +
                        f"(got {pin_label}) on {self.names.get_name_string(dev)}"
                    )
                    self.error_flag = False
                    return False
            else:
                # any other device has exactly one unnamed output
                # so “.Q” is illegal
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
        """Check monitors syntax and makes monitor for each signal."""
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
            # add output signal to monitor list
            local_monitors.append(output_signal)

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

        # call make monitors
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
        """
        Check input pin name is vaild.

        Valid input names are: 'DATA' | 'SET' | 'CLR' | 'CLK' | 'I' pin_number.
        """
        if self.symbol.type in [self.scanner.NAME, self.scanner.KEYWORD]:
            text = self.names.get_name_string(self.symbol.id).upper()
            if text[0] == 'I':
                # NOTE - This might be possible to do using pin number but
                # it is easier to do like this as I16 is read as one symbol
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
        """Check output pin name is Q or QBAR."""
        if self.symbol.type in (self.scanner.NAME, self.scanner.KEYWORD):
            text = self.names.get_name_string(self.symbol.id).upper()
            if text in ('Q', 'QBAR'):
                self._advance()
                return (text, None)
        self._error("invalid pin name")
        return None

    #  pin_number 1–16 (inclusive)
    def _pin_number(self):
        """Check pin number is between 1 and 16."""
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
        """Check integer = non empty sequence of digits."""
        if self.symbol.type != self.scanner.NUMBER:
            self._error("integer expected")
            return 0
        value = self.symbol.id
        self._advance()
        return value

    #  device_name = NAME token
    def _device_name(self):
        """Check device_name = NAME token."""
        #print("name", self.symbol.type==self.scanner.NAME)
        #print(self.names.get_name_string(self.symbol.id))
        if self.symbol.type != self.scanner.NAME:
            print("this is not where the second error is flagged")
            self._error("device identifier expected")
            return None
        name_id = self.symbol.id
        self._advance()
        return name_id
