from pandas import value_counts
from expr import *
import _token

class Interpreter(Visitor):
    def interpret(self, statements):
        from pylox import runtimeError
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as error: 
            runtimeError(error)

    def evaluate(self, expr):
        return expr.accept(self)
    
    def execute(self, stmt):
        stmt.accept(self)

    def stringify(self, ob):
        if ob is None:
            return "nil"
        if isinstance(ob, float):
            text = str(ob)
            if text.endswith('.0'):
                text = text[:-2]
            return text
        return str(ob)

    def visitExpressionStmt(self,stmt):
        self.evaluate(stmt.expression)
        return None

    def visitPrintStmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visitLiteralExpr(self, expr):
        return expr.value
    
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
            raise LoxRuntimeError.RuntimeError(type, "Operands must be two numbers or two strings")
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
        raise LoxRuntimeError.RuntimeError(operator, "Operand must be a number")
    
    
    def check_number_operands(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError.RuntimeError(operator, "Operands must be a number")

class LoxRuntimeError(RuntimeError):
    def RuntimeError(self,token,message):
        super(message)
        self.token = token
