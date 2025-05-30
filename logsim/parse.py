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
        """Initialise constants."""
        self.scanner = scanner
        self.names = names
        self.devices = devices
        self.network = network  
        self.monitors = monitors
        self.symbol = (None)
        self.error_count = 0

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
            # simple panic‑mode recovery – skip to ';' or '}'
            while (self.symbol.type not in (self.scanner.SEMICOLON, self.scanner.CLOSECURLY) and
                   self.symbol.type != self.scanner.EOF):
                self._advance()
            if self.symbol.type != self.scanner.EOF:
                self._advance()

        # -----------------------------------------------------------------------
    def _error(self, message: str):
        self.error_count += 1
        print(f"Parser error (line {self.line}, col {self.column}): {message}")

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
    
        symbol = self.scanner.get_symbol()
        return True

    def _is_kw(self, kw_id: int) -> bool:
        return self.symbol.type == self.scanner.KEYWORD and self.symbol.id == kw_id

    def _spec(self):
        self._block()
        while self._starts_block():
            self._block()
    
    #  EBNF   block       = devices | connections | monitors ;
    def _block(self):
        if self._is_kw(self.scanner.DEVICES):
            self._devices()
        elif self._is_kw(self.scanner.CONNECTIONS):
            self._connections()
        elif self._is_kw(self.scanner.MONITOR):
            self._monitors()
        else:
            self._error("expected 'DEVICES', 'CONNECTIONS' or 'MONITOR'")
            self._advance()

            #  EBNF   spec        = block , { block } ;
    def _spec(self):
        self._block()
        while self._starts_block():
            self._block()
    
    #  EBNF   block       = devices | connections | monitors ;
    def _block(self):
        if self._is_kw(self.scanner.DEVICES):
            self._devices()
        elif self._is_kw(self.scanner.CONNECTIONS):
            self._connections()
        elif self._is_kw(self.scanner.MONITOR):
            self._monitors()
        else:
            self._error("expected 'DEVICES', 'CONNECTIONS' or 'MONITOR'")
            self._advance()
    #  devices = "DEVICES" "{" dev { dev } "}" ;
    def _devices(self):
        self._expect(self.scanner.KEYWORD, self.scanner.DEVICES)
        self._expect(self.scanner.OPENCURLY)
        self._dev()
        while self.symbol.type == self.scanner.NAME:
            self._dev()
        self._expect(self.scanner.CLOSECURLY)

    #  dev = device_name { "." device_name } '=' device_type ';' ;
    def _dev(self):
        names: List[int] = [self._device_name()]  # first identifier consumed
        while self._accept(self.scanner.COMMA):
            names.append(self._device_name())
        self._expect(self.scanner.EQUALS)
        dev_kind, param = self._device_type()
        self._expect(self.scanner.SEMICOLON)
        # ── semantic action here (e.g. create device(s))
        # for nm in names:
        #     self.devices.make_device(nm, dev_kind, param)

    #  device_type = gate | switch | clock | "DTYPE" | "XOR" ;
    def _device_type(self) -> Tuple[Optional[int], Optional[int]]:
        if self._is_kw(self.scanner.AND) or self._is_kw(self.scanner.NAND) or self._is_kw(self.scanner.NOR) or self._is_kw(self.scanner.OR):
            return self._gate()
        elif self.symbol.type == self.scanner.NUMBER and self.symbol.id in (0, 1):
            return self._switch()
        # double check if this is the implementation of switch
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
        gate_kw = self.symbol.id  # remember which gate
        self._advance()
        self._expect(self.scanner.OPENBRAC)
        pins = self._pin_number()
        self._expect(self.scanner.CLOSEBRAC)
        return (self.devices.GATE, (gate_kw, pins))

    #  switch = binary ;   binary = '0' | '1'
    def _switch(self):
        value = self.symbol.id  # 0 or 1
        self._advance()
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
    def _connections(self):
        self._expect(self.scanner.KEYWORD, self.scanner.CONNECTIONS)
        self._expect(self.scanner.OPENCURLY)
        self._con()
        while self.symbol.type == self.scanner.NAME:
            self._con()
        self._expect(self.scanner.CLOSECURLY)

    #  con = signal '->' signal ';' ;
    def _con(self):
        left = self._signal()
        self._expect(self.scanner.ARROW)
        right = self._signal()
        self._expect(self.scanner.SEMICOLON)
        # ── semantic action here (e.g. connect signals)
        # self.network.make_connection(left, right)

    #  signal = device_name [ '.' pin_name ] ;
    def _signal(self):
        dev = self._device_name()
        pin: Optional[int] = None
        if self._accept(self.scanner.FULLSTOP):
            pin = self._pin_name()
        return (dev, pin)

    # ───────────────────────────────────────────────────────── MONITOR block
    #  monitors = "MONITOR" '{' signal { ',' signal } ';' '}' ;
    def _monitors(self):
        self._expect(self.scanner.KEYWORD, self.scanner.MONITOR)
        self._expect(self.scanner.OPENCURLY)
        self._signal()
        while self._accept(self.scanner.COMMA):
            if self.symbol.type != self.scanner.CLOSECURLY:
                self._signal()
        self._expect(self.scanner.CLOSECURLY)

    # ──────────────────────────────────────────────────────────── primitives
    #  pin_name = 'DATA' | 'SET' | 'CLR' | 'CLK' | 'Q' | 'QBAR' | 'I' pin_number ;
    def _pin_name(self):
        if self.symbol.type in (self.scanner.NAME, self.scanner.KEYWORD):
            text = self.names.get_name_string(self.symbol.id).upper()
            self._advance()
            if text == 'I':
                num = self._pin_number()
                return ('I', num)
            elif text in ('DATA', 'SET', 'CLR', 'CLK', 'Q', 'QBAR'):
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
