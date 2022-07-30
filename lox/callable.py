from _return import ReturnJmp
from environment import Environment

class LoxCallable:
    pass

class LoxFunction(LoxCallable):
    def __init__(self, decl, closure):
        self.closure = closure
        self.declaration = decl

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for i in range(len(arguments)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnJmp as r:
            return r.value
        return None

    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        return "<fn " + self.declaration.name.lexeme + ">"
