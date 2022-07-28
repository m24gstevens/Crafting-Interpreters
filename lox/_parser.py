from _token import *
from expr import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        try:
            return self.expression()
        except ParseError:
            return None
    
    def expression(self):
        return self.equality()
    
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
        return self.primary()
    
    def primary(self):
        if self.match(FALSE):
            return Literal(False)
        if self.match(TRUE):
            return Literal(True)
        if self.match(NIL):
            return Literal(None)
        if self.match(NUMBER, STRING):
            return Literal(self.previous().literal)
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
        
