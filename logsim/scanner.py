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
        self.file = open(path, 'r', encoding='utf-8')
        self.current_char = self.file.read(1)
        self.names = names
        self.comment_opened = False  # True if a multi-line comment is open
        self.comment_opened_line = None
        self.comment_opened_column = None
        # NOTE If you need to add a symbol type, increment the range
        self.symbol_type_list = [self.KEYWORD, self.SEMICOLON, self.EQUALS,
                                 self.COMMA,  self.NUMBER, self.NAME, self.EOF,
                                 self.ARROW, self.FULLSTOP, self.OPENCURLY,
                                 self.CLOSECURLY, self.OPENBRAC,
                                 self.CLOSEBRAC] = range(13)

        # NOTE If you are adding a keyword, append it to this list
        self.keywords_list = ["DEVICES", "CONNECTIONS", "MONITOR",
                              "AND", "OR", "NAND", "NOR", "XOR", "DTYPE",
                              "CLOCK","SIGGEN", "SWITCH"]

        # Add the new keyword here aswell
        [self.DEVICES, self.CONNECTIONS, self.MONITOR,
         self.AND, self.OR, self.NAND, self.NOR, self.XOR, self.DTYPE,
         self.CLOCK,self.SIGGEN, self.SWITCH] = self.names.lookup(self.keywords_list)

    def skip_whitespace(self, line, column):
        """Skip whitespace characters in the file."""
        # Skip whitespace characters
        while self.current_char.isspace() or self.current_char == '\n':
            # If we encounter a newline, reset column counter
            # and increment line
            if self.current_char == '\n':
                line += 1
                column = 0
            else:
                column += 1
            self.current_char = self.file.read(1)
        return line, column

    def skip_comments(self, line, column):
        """Skip comments in the file."""
        # Skip single line comments
        if self.current_char == '#':
            # single lines terminate with newline or EOF
            while self.current_char not in ('\n', ''):
                self.current_char = self.file.read(1)
                if self.current_char == '\n':
                    line += 1
                    column = 0
                    self.current_char = self.file.read(1)
                    break

        # Skip multi-line comments
        elif self.current_char == '/':
            next_char = self.file.read(1)
            if next_char == '*':
                self.comment_opened = True
                self.comment_opened_line = line
                self.comment_opened_column = column
                prev = None
                # Consume until we see '*' followed by '/'
                while True:
                    self.current_char = self.file.read(1)
                    if self.current_char == '':
                        # EOF reached without closing comment
                        break
                    # Track newlines
                    if self.current_char == '\n':
                        line += 1
                        column = 0
                    # If previous was '*' and current is '/', comment is closed
                    if prev == '*' and self.current_char == '/':
                        # set current_char to the next character after '/'
                        self.comment_opened = False
                        self.current_char = self.file.read(1)
                        break
                    prev = self.current_char
        return line, column

    def get_name(self, column):
        """Read a sequence of characters and return it as a string."""
        name = ''
        # Names can only contain alphanumeric characters and underscores
        while self.current_char.isalnum() or self.current_char == '_':
            name += self.current_char
            column += 1
            self.current_char = self.file.read(1)
        return name, column

    def get_number(self, column):
        """Read a sequence of digits and return it as an integer."""
        number = ''
        while self.current_char.isdigit():
            number += self.current_char
            column += 1
            self.current_char = self.file.read(1)
        return int(number), column

    def advance(self, column):
        """Advance to the next character in the file."""
        self.current_char = self.file.read(1)
        return column + 1

    def get_symbol(self, line, column):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        # skip whitespace and comments before reading the next character
        line, column = self.skip_whitespace(line, column)
        while self.current_char == '#' or self.current_char =='/':
            line, column = self.skip_comments(line, column)
        line, column = self.skip_whitespace(line, column)
        symbol.line = line
        symbol.column = column

        if self.current_char == '':
            # End of file
            symbol.type = self.EOF
        elif self.current_char.isalpha():
            name_string, column = self.get_name(column)
            # check if the name is a keyword or an identifier
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])
        elif self.current_char.isdigit():
            # Read a number and set the symbol type to NUMBER
            symbol.type = self.NUMBER
            symbol.id, column = self.get_number(column)
        elif self.current_char == ',':
            symbol.type = self.COMMA
            column = self.advance(column)
        elif self.current_char == ';':
            symbol.type = self.SEMICOLON
            column = self.advance(column)
        elif self.current_char == '=':
            symbol.type = self.EQUALS
            column = self.advance(column)
        elif self.current_char == '{':
            symbol.type = self.OPENCURLY
            column = self.advance(column)
        elif self.current_char == '}':
            symbol.type = self.CLOSECURLY
            column = self.advance(column)
        elif self.current_char == '(':
            symbol.type = self.OPENBRAC
            column = self.advance(column)
        elif self.current_char == ')':
            symbol.type = self.CLOSEBRAC
            column = self.advance(column)
        elif self.current_char == '.':
            symbol.type = self.FULLSTOP
            column = self.advance(column)
        elif self.current_char == '-':
            column = self.advance(column)
            if self.current_char == '>':
                symbol.type = self.ARROW
                column = self.advance(column)
            else:
                # symbol type is None in the case of just '-'
                pass
        else:
            column = self.advance(column)

        return symbol, line, column

    def get_line(self, line_number):
        """Return a specific line of an input file."""
        self.file.seek(0)  # Reset file pointer to the beginning
        for current_line_number, line in enumerate(self.file, start=1):
            if current_line_number == line_number:
                # Return the line without trailing newline
                return line.rstrip('\n')
        return None  # If the line number is out of range

    def print_error_line(self, line, column):
        """Print the line with a caret (^) underneath the character at error_pos."""
        self.file.seek(0)
        num_lines = len(self.file.readlines())
        if line>num_lines:
            line = num_lines
        if num_lines == 0:
            print("Error: File is empty.")
            return
        self.file.seek(0)
        line_text = self.get_line(line)
        print(line_text)
        if 0 <= column and column < len(line_text):
            print(" " * (column) + "^")
        else:
            print(" " * len(line_text.rstrip())
                  + "^ (error position out of bounds)")
