from expr import *
from _token import Token, MINUS, STAR

class AstPrinter(Visitor):
    def print(self, expr):
        return expr.accept(self)

    def parenthesize(self, name, *args):
        string = ""
        string += "(" + name
        for arg in args:
            string += " "
            string += arg.accept(self)
        string += ")"
        return string
    
    def visitBinaryExpr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
    def visitGroupingExpr(self, expr):
        return self.parenthesize("group", expr.expression)

    def visitLiteralExpr(self, expr):
        if expr.value == None:
            return "nil"
        return str(expr.value)

    def visitUnaryExpr(self,expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)

def main():
    expression = Binary(Unary(Token(MINUS, '-', None, 1), Literal(123)),
                            Token(STAR, "*", None, 1),
                            Grouping(Literal(45.67)))
    print(AstPrinter().print(expression))

if __name__ == "__main__":
    main()