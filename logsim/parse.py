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
    def _error(self, message: str):
        self.error_count += 1
        self.error_flag = True
        # This is a very scuffed way of not printing error messages if we have already reached EOF
        if self.symbol.type!=self.scanner.EOF:
            self.scanner.print_error_line(self.symbol.line, self.symbol.column)
            print(f"Parser error (line {self.symbol.line}, col {self.symbol.column}): {message}")
        else:
            return
        while (self.symbol.type not in self.stopping_set and
                self.symbol.type != self.scanner.EOF):
            print(self.symbol.type)
            if self.symbol.type == self.scanner.NAME:
                print(self.names.get_name_string(self.symbol.id))
            self._advance()
        if self.symbol.type == self.scanner.EOF:
            print("Error recovery was not possible, end of file reached")
        else:
            self._advance()

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
        guitest = False
        if guitest:
            return True
        else:
            self._spec()

    def _is_kw(self, kw_id: int) -> bool:
        return self.symbol.type == self.scanner.KEYWORD and self.symbol.id == kw_id
    
    #  EBNF   spec        = devices, connections, monitors ;
    def _spec(self):
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.DEVICES:
            self._devices()
        else:
            self._error("Expected DEVICEES block")
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.CONNECTIONS:
            self._connections()
        else:
            self._error("Expected CONNECTIONS block")
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.MONITOR:
            self._monitors()
        else:
            self._error("Expected MONITORS block")

    #  devices = "DEVICES" "{" dev { dev } "}" ;
    def _devices(self):
        self._expect(self.scanner.KEYWORD, self.scanner.DEVICES)
        self._expect(self.scanner.OPENCURLY)
        self.stopping_set = [self.scanner.CLOSECURLY, self.scanner.SEMICOLON]
        self._dev()
        # BUG - If you put a none name symbol then it expects a 
        # closecurly as the next symbol but skips to the semicolon so should just
        # continue parsing
        while self.symbol.type != self.scanner.CLOSECURLY:
            if self.symbol.type == self.scanner.NAME:
                self._dev()
            else:
                self._error("device identifier expected")

        self.stopping_set = [self.scanner.CLOSECURLY]
        self._expect(self.scanner.CLOSECURLY)
        self.stopping_set = []

    #  dev = device_name { "," device_name } '=' device_type ';' ;
    def _dev(self):
        #if an error flag is raised then need to not run the rest
        names_list: List[int] = [self._device_name()]  # first identifier consumed
        if self.error_flag:
            self.error_flag = False
            return False
        while self._accept(self.scanner.COMMA):
            names_list.append(self._device_name())
            if self.error_flag:
                self.error_flag = False
                return False
        self._expect(self.scanner.EQUALS)
        if self.error_flag:
            self.error_flag = False
            return False
        dev_kind, param = self._device_type()
        if self.error_flag:
            self.error_flag = False
            return False
        self._expect(self.scanner.SEMICOLON)
        if self.error_flag:
            self.error_flag = False
            return False
        return True
        # ── semantic action here (e.g. create device(s))
        # for nm in names:
        #     self.devices.make_device(nm, dev_kind, param)

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
            self._advance()
            return (None, None)

    #  gate = ( "AND" | "NAND" | "NOR" | "OR" ) '(' pin_number ')' ;
    def _gate(self):
        # BUG - devices doesn't have a GATE attribute
        gate_kw = self.symbol.id  # remember which gate
        self._advance()
        self._expect(self.scanner.OPENBRAC)
        pins = self._pin_number()
        self._expect(self.scanner.CLOSEBRAC)
        return (gate_kw, pins)

    #  switch = "SWTICH", "(", binary, ")" ;   binary = '0' | '1';
    def _switch(self):
        self._expect(self.scanner.KEYWORD, self.scanner.SWITCH)
        self._expect(self.scanner.OPENBRAC)
        value = self.symbol.id  # 0 or 1
        if value not in [0, 1]:
            self._error("Expected binary input")
        self._advance()
        self._expect(self.scanner.CLOSEBRAC)
        return (self.devices.SWITCH, value)

    #  clock = "CLOCK" '(' integer ')' ;
    def _clock(self):
        self._expect(self.scanner.KEYWORD, self.scanner.CLOCK)
        self._expect(self.scanner.OPENBRAC)
        period = self._integer()
        self._expect(self.scanner.CLOSEBRAC)
        return (self.devices.CLOCK, period)

    # ─────────────────────────────────────────────────────── CONNECTIONS block
    #  connections = "CONNECTIONS" '{' con { con } '}' ;
    # BUG - connections is not currently working, i will fix it on my next push
    def _connections(self):
        self._expect(self.scanner.KEYWORD, self.scanner.CONNECTIONS)
        self._expect(self.scanner.OPENCURLY)
        self.stopping_set = [self.scanner.CLOSECURLY, self.scanner.SEMICOLON]
        self._con()
        while self.symbol.type == self.scanner.NAME:
            self._con()
        self.stopping_set = [self.scanner.CLOSECURLY]
        self._expect(self.scanner.CLOSECURLY)
        self.stopping_set = []

    #  con = signal '->' signal ';' ;
    def _con(self):
        output_signal = self._output_signal()
        self._expect(self.scanner.ARROW)
        input_signal = self._input_signal()
        self._expect(self.scanner.SEMICOLON)
        # ── semantic action here (e.g. connect signals)
        # self.network.make_connection(left, right)

    #  input_signal = device_name, ".", input_pin_name;
    def _input_signal(self):
        dev = self._device_name()
        self._expect(self.scanner.FULLSTOP)
        pin = self._input_pin_name()
        return (dev, pin)

    # output_signal = device_name, [".", output_pin_name];
    def _output_signal(self):
        dev = self._device_name()
        pin: Optional[int] = None
        if self._accept(self.scanner.FULLSTOP):
            pin = self._output_pin_name()
        return (dev, pin)
    
    # ───────────────────────────────────────────────────────── MONITOR block
    #  monitors = "MONITOR" '{' signal { ',' signal } ';' '}' ;
    def _monitors(self):
        self._expect(self.scanner.KEYWORD, self.scanner.MONITOR)
        self._expect(self.scanner.OPENCURLY)
        self.stopping_set = [self.scanner.CLOSECURLY, self.scanner.SEMICOLON]
        self._output_signal()
        while self._accept(self.scanner.COMMA):
            if self.symbol.type != self.scanner.CLOSECURLY:
                self._output_signal()
        self.stopping_set = [self.scanner.CLOSECURLY]
        self._expect(self.scanner.SEMICOLON)
        self._expect(self.scanner.CLOSECURLY)
        self.stopping_set = []

    # ──────────────────────────────────────────────────────────── primitives
    # input_pin_name = 'DATA' | 'SET' | 'CLR' | 'CLK' | 'I' pin_number ;
    def _input_pin_name(self):
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
                    self._error("pin number out of range (1‑16)")
                    return (None, None)
                self._advance()
                return ('I', num)
            elif text in ('DATA', 'SET', 'CLR', 'CLK'):
                self._advance()
                return (text, None)
        self._error("invalid pin name")
        return None

    # output_pin_name = 'Q' | 'QBAR';
    def _output_pin_name(self):
        if self.symbol.type in (self.scanner.NAME, self.scanner.KEYWORD):
            text = self.names.get_name_string(self.symbol.id).upper()
            if text in ('Q', 'QBAR'):
                return (text, None)
        self._error("invalid pin name")
        return None

    #  pin_number 1–16 (inclusive)
    def _pin_number(self):
        if self.symbol.type != self.scanner.NUMBER:
            self._error("pin number expected")
            return None
        value = self.symbol.id
        if not (1 <= value <= 16):
            self._error("pin number out of range (1‑16)")
        self._advance()
        return value

    #  integer = non‑empty sequence of digits (scanner already returns NUMBER)
    def _integer(self):
        if self.symbol.type != self.scanner.NUMBER:
            self._error("integer expected")
            return 0
        value = self.symbol.id
        self._advance()
        return value

    #  device_name = NAME token
    def _device_name(self):
        if self.symbol.type != self.scanner.NAME:
            self._error("device identifier expected")
            return None
        name_id = self.symbol.id
        self._advance()
        return name_id


    """
        def non_terminal_symbol(symbol, expected):
            Check if the symbol is a non-terminal symbol.
            if symbol != expected:
                self.scanner.error(f"Expected {expected}, got {symbol}")
                return False
            return True
        return True

        def con(self):
            self.scanner.NAME
            if self.scanner.get_symbol().type == self.scanner.ARROW:
                self.symbol = self.scanner.get_symbol()
                self.symbol.NAME
            elif self.scanner.get_symbol().type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
                self.symbol.NAME               
            else:
                self.error()
                #return False

        def connections(self):
            if (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.CONNECT_ID):
                self.symbol = self.scanner.get_symbol()

                if self.symbol.type == self.scanner.OPENCURLY:
                    self.symbol = self.scanner.get_symbol()
                    self.con()
                    while self.symbol.type == self.scanner.COMMA:
                        self.symbol = self.scanner.get_symbol()
                        self.con()        
                
                if self.symbol.type == self.scanner.SEMICOLON:
                    self.symbol = self.scanner.get_symbol()
                else:
                    self.error()
                    #return False
            else:
                self.error()
                #return False    

        """
    #if out of scanner = "NAME"
    # LOOK AT NEXT SYMBOL = "ARROW"
