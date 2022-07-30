import sys
from _token import Scanner, EOF
from _parser import Parser
from ast_printer import AstPrinter
from interpreter import Interpreter
from expr import Expr

had_error = False
had_runtime_error = False
interpreter = Interpreter()

def run_file(file):
    with open(file, 'r') as f:
        run(f.read())
    if had_error:
        sys.exit(2)
    if had_runtime_error:
        sys.exit(3)

def run_prompt():
    global had_error
    while 1:
        had_error = False
        line = input("> ")
        scanner = Scanner(line)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        syntax = parser.parse_repl()
        if had_error:
            continue    # Ignore syntax errors
        if isinstance(syntax, list):
            interpreter.interpret(syntax)
        elif isinstance(syntax, Expr):
            result = interpreter.interpret_expr(syntax)
            if result is not None:
                print(f"= {result}")


def run(source):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()
    if had_error:
        return
    interpreter.interpret(statements)

def report(line, where, message):
    sys.stderr.write(f"[line {line}] Error{where}: {message}")

def error(token, message):
    if token.type == EOF:
        report(token.line, " at end", message)
    else:
        report(token.line, " at '" + token.lexeme + "'", message)

def runtimeError(error):
    sys.stderr.write(str(error) + "\n[line " + str(error.token.line) + "]")
    global had_runtime_error
    had_runtime_error = True