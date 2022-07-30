import pylox

(LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE, \
COMMA, DOT, MINUS, PLUS, SEMICOLON, SLASH, STAR,
BANG, BANG_EQUAL,EQUAL, EQUAL_EQUAL, \
 GREATER, GREATER_EQUAL, LESS, LESS_EQUAL, \
 IDENTIFIER, STRING, NUMBER, \
 AND, BREAK, CLASS, ELSE, FALSE, FUN, FOR, IF, NIL, OR, \
 PRINT, RETURN, SUPER, THIS, TRUE, VAR, WHILE, \
 EOF) = range(40)

class Token:
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    def __str__(self):
        return str(self.type) + " " + str(self.lexeme) + " " + str(self.literal)

class Scanner:
    keywords = {"and": AND, "class": CLASS, "else": ELSE, "false": FALSE,
    "for": FOR, "fun":FUN, "if":IF, "nil":NIL, "or":OR,
    "print":PRINT, "return":RETURN, "super":SUPER, "this":THIS, "true":TRUE, "var":VAR, "while":WHILE, "break":BREAK}
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(EOF,"",None,self.line))
        return self.tokens
    def is_at_end(self):
        return self.current >= len(self.source)
    def scan_token(self):
        c = self.advance()
        if c == '(':
            self.add_token_single(LEFT_PAREN)
        elif c == ')':
            self.add_token_single(RIGHT_PAREN)
        elif c == '{':
            self.add_token_single(LEFT_BRACE)
        elif c == '}':
            self.add_token_single(RIGHT_BRACE)
        elif c == ',':
            self.add_token_single(COMMA)
        elif c == '.':
            self.add_token_single(DOT)
        elif c == '-':
            self.add_token_single(MINUS)
        elif c == '+':
            self.add_token_single(PLUS)
        elif c == ';':
            self.add_token_single(SEMICOLON)
        elif c == '*':
            self.add_token_single(STAR)
        elif c == '!':
            self.add_token_single(BANG_EQUAL if self.match('=') else BANG)
        elif c == '=':
            self.add_token_single(EQUAL_EQUAL if self.match('=') else EQUAL)
        elif c == '<':
            self.add_token_single(LESS_EQUAL if self.match('=') else LESS)
        elif c == '>':
            self.add_token_single(GREATER_EQUAL if self.match('=') else GREATER)
        elif c == '/':
            if (self.match('/')):
                while (self.peek() != '\n' and not self.is_at_end()):
                    self.advance()
            else:
                self.add_token_single(SLASH)
        elif c in ' \r\t':
            pass
        elif c == '\n':
            self.line += 1
        elif c == '"':
            self.string()
        else:
            if (c.isnumeric()):
                self.number()
            elif (c.isalpha()):
                self.identifier()
            else:
                pylox.error(self.line, f"Unexpected character: {c}")


    def advance(self):
        self.current += 1
        return self.source[self.current - 1]
    def peek(self):
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]
    def add_token_single(self, type):
        self.add_token(type, None)
    def add_token(self, type, literal):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))
    def match(self, expected):
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True
    def string(self):
        while (self.peek() != '"' and not self.is_at_end()):
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        if self.is_at_end():
            pylox.error(self.line, "Unterminated string")
            return
        self.advance()
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(STRING, value)
    def number(self):
        while self.peek().isnumeric():
            self.advance()
        if (self.peek() == '.' and self.peek_next().isnumeric()):
            self.advance()
            while self.peek().isnumeric():
                self.advance()
        self.add_token(NUMBER, float(self.source[self.start:self.current]))
    def identifier(self):
        while self.peek().isalnum():
            self.advance()
        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text)
        if not token_type:
            token_type = IDENTIFIER
        self.add_token_single(token_type)

