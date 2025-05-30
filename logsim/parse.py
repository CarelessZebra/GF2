"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


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
         
    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
    
        symbol = self.scanner.get_symbol()

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




        def non_terminal_symbol(symbol, expected):
            """Check if the symbol is a non-terminal symbol."""
            if symbol != expected:
                self.scanner.error(f"Expected {expected}, got {symbol}")
                return False
            return True
        return True
    


    #if out of scanner = "NAME"
    # LOOK AT NEXT SYMBOL = "ARROW"
