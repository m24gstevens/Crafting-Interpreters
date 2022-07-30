from stmt import *
from expr import *
from callable import LoxCallable, LoxFunction
import _token
from environment import Environment
from _return import ReturnJmp
import time

class Interpreter(Visitor):
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        Clock = LoxCallable
        Clock.arity = lambda : 0
        Clock.call = lambda interpreter, arguments: float(time.time())
        Clock.__str__ = lambda : "<native fn>"
        self.globals.define("clock", Clock)

    def interpret(self, statements):
        from pylox import runtimeError
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as error: 
            runtimeError(error)

    # For the "shell-like" interpreter
    def interpret_expr(self, expr):
        try:
            value = self.evaluate(expr)
            return self.stringify(value)
        except LoxRuntimeError as error:
            from pylox import runtimeError
            runtimeError(error)
            return None

    def evaluate(self, expr):
        return expr.accept(self)
    
    def execute(self, stmt):
        stmt.accept(self)

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def stringify(self, ob):
        if ob is None:
            return "nil"
        if isinstance(ob, float):
            text = str(ob)
            if text.endswith('.0'):
                text = text[:-2]
            return text
        return str(ob)

    def visitBlockStmt(self,stmt):
        self.execute_block(stmt.statements, Environment(self.environment))
        return None

    def visitExpressionStmt(self,stmt):
        self.evaluate(stmt.expression)
        return None

    def visitFunctionStmt(self, stmt):
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
        return None

    def visitIfStmt(self, stmt):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None

    def visitPrintStmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visitReturnStmt(self, stmt):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise ReturnJmp(value)

    def visitVarStmt(self, stmt):
        value = None
        if stmt.initializer != None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)
        return None

    def visitWhileStmt(self, stmt):
        try:
            while(self.is_truthy(self.evaluate(stmt.condition))):
                self.execute(stmt.body)
        except BreakException:
            pass
        return None

    def visitBreakStmt(self, stmt):
        raise BreakException()

    def visitAssignExpr(self, expr):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visitLiteralExpr(self, expr):
        return expr.value

    def visitLogicalExpr(self, expr):
        left = self.evaluate(expr.left)
        if expr.operator.type == _token.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        return self.evaluate(expr.right)

    
    def visitGroupingExpr(self, expr):
        return self.evaluate(expr.expression)
    
    def visitUnaryExpr(self, expr):
        right = self.evaluate(expr.right)
        type = expr.operator.type
        if type == _token.MINUS:
            self.check_number_operand(type, right)
            return -float(right)
        elif type == _token.BANG:
            return not self.is_truthy(right)
        return None

    def visitVariableExpr(self, expr):
        return self.environment.get(expr.name)

    def visitBinaryExpr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        type = expr.operator.type
        if type == _token.MINUS:
            self.check_number_operands(type, left, right)
            return float(left) - float(right)
        elif type == _token.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            if isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)
            raise LoxRuntimeError(type, "Operands must be two numbers or two strings")
        elif type == _token.SLASH:
            self.check_number_operands(type, left, right)
            return float(left) / float(right)
        elif type == _token.STAR:
            self.check_number_operands(type, left, right)
            return float(left) * float(right)
        elif type == _token.GREATER:
            self.check_number_operands(type, left, right)
            return float(left) > float(right)
        elif type == _token.GREATER_EQUAL:
            self.check_number_operands(type, left, right)
            return float(left) >= float(right)
        elif type == _token.LESS:
            self.check_number_operands(type, left, right)
            return float(left) < float(right)
        elif type == _token.LESS_EQUAL:
            self.check_number_operands(type, left, right)
            return float(left) <= float(right)
        elif type == _token.EQUAL_EQUAL:
            return self.is_equal(left, right)
        elif type == _token.BANG_EQUAL:
            return not self.is_equal(left, right)

    def visitCallExpr(self, expr):
        callee = self.evaluate(expr.callee)
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes")
        if len(arguments) != callee.arity():
            raise LoxRuntimeError(expr.paren, f"Expected {callee.arity()} arguments but got {len(arguments)}.")
        return callee.call(self, arguments)
        

    def is_truthy(self, object):
        if object is None:
            return False
        elif isinstance(object, bool):
            return object
        return True

    def is_equal(self, a, b):
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    def check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return
        raise LoxRuntimeError(operator, "Operand must be a number")
    
    
    def check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError(operator, "Operands must be a number")

class LoxRuntimeError(RuntimeError):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token

class BreakException(Exception):
    pass
