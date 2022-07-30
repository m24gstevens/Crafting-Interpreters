from _return import ReturnJmp
from environment import Environment

class LoxCallable:
    pass

class LoxFunction(LoxCallable):
    def __init__(self, name, decl, closure, is_initializer):
        self.name = name
        self.closure = closure
        self.declaration = decl
        self.is_initializer = is_initializer

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for i in range(len(arguments)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnJmp as r:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return r.value
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None

    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        if self.name is None:
            return "<fn>"
        return "<fn " + self.name + ">"

    def bind(self, instance, name):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(name, self.declaration, environment, self.is_initializer)

class LoxClass(LoxCallable):
    def __init__(self, name, superclass, methods):
        self.name = name
        self.methods = methods
        self.superclass = superclass
    def __str__(self):
        return self.name

    def call(self, interpreter, arguments):
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance, "init").call(interpreter, arguments)
        return instance

    def arity(self):
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        if self.superclass is not None:
            return self.superclass.find_method(name)
        return None

class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}
    def __str__(self):
        return self.klass.name + " instance"
    def get(self,name):
        if name.lexeme in self.fields:
            return self.fields.get(name.lexeme)
        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self, name.lexeme)
        from interpreter import LoxRuntimeError
        raise LoxRuntimeError(name, f"Undefined property {name.lexeme}.")

    def set(self, name, value):
        self.fields[name.lexeme] = value
    
