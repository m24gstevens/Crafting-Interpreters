import sys
from _token import Scanner, EOF
from _parser import Parser
from ast_printer import AstPrinter

had_error = False

def run_file(file):
    with open(file, 'r') as f:
        run(f.read())
    if had_error:
        sys.exit(2)

def run_prompt():
    while 1:
        line = input("> ")
        if not line:
            break
        run(line)
        global had_error
        had_error = False


def run(source):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    expression = parser.parse()
    if had_error:
        return
    print(AstPrinter().print(expression))

def report(line, where, message):
    sys.stderr.write(f"[line {line}] Error{where}: {message}")

def error(token, message):
    if token.type == EOF:
        report(token.line, " at end", message)
    else:
        report(token.line, " at '" + token.lexeme + "'", message)