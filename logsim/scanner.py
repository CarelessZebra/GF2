"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None
        self.line = None
        self.column = None


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        self.current_char = None
        self.file = open(path, 'r')

        self.names = names
        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.EQUALS, self.KEYWORD, self.NUMBER, self.NAME, self.EOF, self.ARROW] = range(7)
        #I'm not sure if this is every keyword defined in the grammar. 
        self.keywords_list = ["DEVICES", "CONNECTIONS", "MONITOR", "AND", "OR", "NAND", "XOR", "DTYPE", "CLK"]
        [self.DEVICES, self.CONNECTIONS, self.MONITOR, self.AND, self.OR, self.NAND, self.XOR, self.DTPE, self.CLK] = self.names.lookup(self.keywords_list)
    
    def skip_whitespace(self):
        """Skip whitespace characters in the file."""
        self.current_char = self.file.read(1)
        while self.current_char.isspace():
            self.current_char = self.file.read(1)

    def get_name(self):
        """Read a sequence of characters and return it as a string."""
        name = ''
        while self.current_char.isalnum() or self.current_char == '_':
            name += self.current_char
            self.current_char = self.file.read(1)
        return name
    
    def get_numebr(self):
        """Read a sequence of digits and return it as an integer."""
        number = ''
        while self.current_char.isdigit():
            number += self.current_char
            self.current_char = self.file.read(1)
        return int(number)

    def advance(self):
        """Advance to the next character in the file."""
        self.current_char = self.file.read(1)
    
    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        #WON'T WORK TILL NAMES IS IMPLEMENTED
        symbol = Symbol()
        #skip whitespace before reading the next character
        self.skip_whitespace()
        if self.current_char == '':
            # End of file
            symbol.type = self.EOF
        elif self.current_char.isalpha():
            name_string = self.get_name()
            #check if the name is a keyword or an identifier
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.IDENTIFIER
            [symbol.id] = self.names.lookup([name_string])
        elif self.current_char.isdigit():
            # Read a number and set the symbol type to NUMBER
            symbol.type = self.NUMBER
            symbol.id = self.get_numebr()
        elif self.current_char == ',':
            symbol.type = self.COMMA
            self.advance()
        elif self.current_char == ';':
            symbol.type = self.SEMICOLON
            self.advance()
        elif self.current_char == '=':
            symbol.type = self.EQUALS
            self.advance()
        elif self.current_char == '-':
            #I can't test properly until the names module is implemented but expected
            # behaviour is that if you have -DEVICES then it will have - as a None symbol
            # and DEVICES treated properly as a keyword, and -> is treated as an arrow.
            self.advance()
            if self.current_char == '>':
                symbol.type = self.ARROW
                self.advance()
            else:
                pass
        else:
            self.advance()
        return symbol
        



        
