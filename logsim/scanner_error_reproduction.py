"""This is a reproduction of an error with scanner that means print_error_line should only be called after all the file has been read"""
from names import Names
from scanner import Scanner

names = Names()
scanner = Scanner("test_full_adder.txt", names)
symbol, line, col = scanner.get_symbol(1,0)
while symbol.type != None:
    symbol, line, col = scanner.get_symbol(line,col)
    if symbol.type == scanner.NAME:
        print(names.get_name_string(symbol.id))
scanner.print_error_line(symbol.line, symbol.column)
while symbol.type != scanner.SEMICOLON:
    symbol, line, col = scanner.get_symbol(line,col)
    if symbol.type == scanner.NAME:
        print(names.get_name_string(symbol.id))
"""
while symbol.type != None:
    symbol, line, col = scanner.get_symbol(line,col)
    if symbol.type == scanner.NAME:
        print(names.get_name_string(symbol.id))
"""