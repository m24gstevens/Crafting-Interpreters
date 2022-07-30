from tkinter import LEFT, RIGHT
from _token import *
from expr import *
from stmt import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.found_expression = False
        self.allow_expression = False
        self.loop_depth = 0

    def parse_repl(self):
        self.allow_expression = True
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
            if self.found_expression:
                last = statements[-1]
                return last.expression
            self.allow_expression = False
        return statements

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements
        
    def statement(self):
        if self.match(FOR):
            return self.for_statement()
        if self.match(IF):
            return self.if_statement()
        if self.match(PRINT):
            return self.print_statement()
        if self.match(RETURN):
            return self.return_statement()
        if self.match(WHILE):
            return self.while_statement()
        if self.match(BREAK):
            return self.break_statement()
        if self.match(LEFT_BRACE):
            return Block(self.block())
        return self.expression_statement()

    def for_statement(self):
        self.consume(LEFT_PAREN, "Expect '(' after 'for'.")
        if self.match(SEMICOLON):
            initializer = None
        elif self.match(VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        condition = None
        if not self.check(SEMICOLON):
            condition = self.expression()
        self.consume(SEMICOLON, "Expect ';' after loop condition")
        increment = None
        if not self.check(RIGHT_PAREN):
            increment = self.expression()
        self.consume(RIGHT_PAREN, "Expect ')' after for clauses")
        try:
            self.loop_depth += 1
            body = self.statement()
            if increment is not None:
                body = Block([body, Expression(increment)])
            if condition is None:
                condition = Literal(True)
            body = While(condition, body)
            if initializer is not None:
                body = Block([initializer, body])
            return body
        finally:
            self.loop_depth -= 1

    def if_statement(self):
        self.consume(LEFT_PAREN, "Expect '(' afer 'if'.")
        condition = self.expression()
        self.consume(RIGHT_PAREN, "Expect ')' after if condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match(ELSE):
            else_branch = self.statement()
        return If(condition, then_branch, else_branch)

    def print_statement(self):
        value = self.expression()
        self.consume(SEMICOLON, "Expected ';' after value.")
        return Print(value)

    def return_statement(self):
        keyword = self.previous()
        value = None
        if not self.check(SEMICOLON):
            value = self.expression()
        self.consume(SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)
    
    def expression_statement(self):
        expr = self.expression()
        if self.allow_expression and self.is_at_end():
            self.found_expression = True
        else:
            self.consume(SEMICOLON, "Expected ';' after expression.")
        return Expression(expr)
    
    def block(self):
        statements = []
        while not self.check(RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def assignment(self):
        expr = self.or_expr()
        if self.match(EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            self.error(equals, "Invalid assignment target.")
        return expr

    def or_expr(self):
        expr = self.and_expr()
        while self.match(OR):
            operator = self.previous()
            right = self.and_expr()
            expr = Logical(expr,operator, right)
        return expr

    def and_expr(self):
        expr = self.equality()
        while self.match(AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        return expr

    def var_declaration(self):
        name = self.consume(IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(EQUAL):
            initializer = self.expression()
        self.consume(SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)
    
    def while_statement(self):
        self.consume(LEFT_PAREN,"Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(RIGHT_PAREN, "Expect ')' after condition.")
        try:
            self.loop_depth += 1
            body = self.statement()
            return While(condition, body)
        finally:
            self.loop_depth -= 1

    def break_statement(self):
        if self.loop_depth == 0:
            self.error(self.previous(), "Must be inside a loop to use 'break'.")
        self.consume(SEMICOLON, "Expect ';' after 'break'.")
        return Break()

    def expression(self):
        return self.assignment()

    def function(self, kind):
        name = self.consume(IDENTIFIER, f"Expect {kind} name.")
        self.consume(LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check(RIGHT_PAREN):
            parameters.append(self.consume(IDENTIFIER, "Expect parameter name"))
            while (self.match(COMMA)):
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume(IDENTIFIER, "Expect parameter name"))
        self.consume(RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(LEFT_BRACE, "Expect '{' before " + kind + " body")
        body = self.block()
        return Function(name, parameters, body)

    def declaration(self):
        try:
            if self.match(FUN):
                return self.function("function")
            if self.match(VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None
    
    def equality(self):
        expr = self.comparison()
        while self.match(BANG_EQUAL, EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(GREATER, GREATER_EQUAL, LESS, LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr
    
    def term(self):
        expr = self.factor()
        while self.match(MINUS, PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(STAR, SLASH):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr
    
    def unary(self):
        if self.match(BANG, MINUS):
            operator = self.previous()
            return Unary(operator, self.unary())
        return self.call()

    def finish_call(self, callee):
        arguments = []
        if not self.check(RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(COMMA):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments")
                arguments.append(self.expression())
        paren = self.consume(RIGHT_PAREN, "Expect ')' after arguments.")
        return Call(callee, paren, arguments)
    
    def call(self):
        expr = self.primary()
        while 1:
            if self.match(LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break
        return expr

    def primary(self):
        if self.match(FALSE):
            return Literal(False)
        if self.match(TRUE):
            return Literal(True)
        if self.match(NIL):
            return Literal(None)
        if self.match(NUMBER, STRING):
            return Literal(self.previous().literal)
        if self.match(IDENTIFIER):
            return Variable(self.previous())
        if self.match(LEFT_PAREN):
            expr = self.expression()
            self.consume(RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        
        raise self.error(self.peek(), "Expect expression.")
        
    
    def match(self, *token_types):
        for type in token_types:
            if self.check(type):
                self.advance()
                return True
        return False
    
    def check(self, type):
        if self.is_at_end():
            return False
        return self.peek().type == type
    
    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self):
        return self.peek().type == EOF
    
    def peek(self):
        return self.tokens[self.current]
    def previous(self):
        return self.tokens[self.current - 1]

    def consume(self, type, message):
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)
    
    def error(self,token, message):
        import pylox
        pylox.error(token, message)
        return ParseError()

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().type == SEMICOLON:
                return
            ptype = self.peek().type
            if ptype in [CLASS, FUN, VAR, FOR, IF, WHILE, PRINT, RETURN]:
                return
            self.advance()

class ParseError(RuntimeError):
    pass
        
