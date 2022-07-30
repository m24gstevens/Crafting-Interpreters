from collections import deque

NONE = 0
CLASS = 1
SUBCLASS = 2
FUNCTION = 1
INITIALIZER = 2
METHOD = 3

class Resolver:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = deque()   # A generalized stack - We use append to push and pop to pop
        self.current_function = NONE
        self.current_class = NONE
    
    def visitBlockStmt(self, stmt):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
        return None

    def visitClassStmt(self, stmt):
        enclosing_class = self.current_class
        self.current_class = CLASS
        self.declare(stmt.name)
        self.define(stmt.name)

        if stmt.superclass is not None and stmt.name.lexeme == stmt.superclass.name.lexeme:
            from pylox import error
            error(stmt.superclass.name, "A class can't inherit from itself.")
        if stmt.superclass is not None:
            self.resolve(stmt.superclass)
        
        if stmt.superclass is not None:
            self.current_class = SUBCLASS
            self.resolve(stmt.superclass)
            self.begin_scope()
            self.scopes[-1]["super"] = True

        self.begin_scope()
        self.scopes[-1]["this"] = True
        for method in stmt.methods:
            declaration = METHOD     # Method type
            if method.name.lexeme == "init":
                declaration = INITIALIZER
            self.resolve_function(method.function, declaration)
        self.end_scope()
        if stmt.superclass is not None:
            self.end_scope()
        self.current_class = enclosing_class
        return None

    def visitExpressionStmt(self, stmt):
        self.resolve(stmt.expression)
        return None

    def visitFunctionStmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt.function, self.current_function)
        return None

    def visitFunctionExpressionExpr(self, expr):
        # For anonymous functions
        self.resolve_function(expr, self.current_function)


    def visitIfStmt(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)

    def visitPrintStmt(self, stmt):
        self.resolve(stmt.expression)
        return None

    def visitReturnStmt(self, stmt):
        if self.current_function is None:
            from pylox import error
            error(stmt.keyword, "Can't return from top level code.")
        if stmt.value is not None:
            if self.current_function == INITIALIZER:
                from pylox import error
                error(stmt.keyword, "Can't return a value from an initializer.")
            self.resolve(stmt.value)
        return None

    def visitBreakStmt(self, stmt):
        return None

    def visitVarStmt(self, stmt):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    def visitWhileStmt(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
        return None

    def visitAssignExpr(self, expr):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)
        return None

    def visitBinaryExpr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    def visitCallExpr(self, expr):
        self.resolve(expr.callee)
        for arg in expr.arguments:
            self.resolve(arg)
        return None

    def visitGetExpr(self, expr):
        self.resolve(expr.object)
        return None

    def visitGroupingExpr(self, expr):
        self.resolve(expr.expression)
        return None

    def visitLiteralExpr(self, expr):
        return None
    
    def visitLogicalExpr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None

    def visitSetExpr(self, expr):
        self.resolve(expr.value)
        self.resolve(expr.object)
        return None

    def visitSuperExpr(self,expr):
        from pylox import error
        if self.current_class == NONE:
            error(expr.keyword, "Can't use 'super' outside of a class.")
        elif self.current_class != SUBCLASS:
            error(expr.keyword, "Can't use 'super' in a class with no superclass.")
        self.resolve_local(expr, expr.keyword)
        return None

    def visitThisExpr(self, expr):
        if self.current_class == NONE:
            # No current class
            from pylox import error
            error(expr.keyword, "Can't use 'this' outside of a class.")
        self.resolve_local(expr, expr.keyword)
        return None

    def visitUnaryExpr(self, expr):
        self.resolve(expr.right)
        return None

    def visitVariableExpr(self, expr):
        if not len(self.scopes) == 0 and self.scopes[-1].get(expr.name.lexeme) == False:
            from pylox import error
            error(expr.name, "Can't read local variable in its own initializer")
        self.resolve_local(expr, expr.name)
        return None

    def declare(self, name):
        if len(self.scopes) == 0:
            return
        if name in self.scopes[-1]:
            from pylox import error
            error(name, "Already a variable with this name in this scope.")
        self.scopes[-1][name.lexeme] = False
    
    def define(self, name):
        if len(self.scopes) == 0:
            return
        self.scopes[-1][name.lexeme] = True
    
    def resolve(self, stmt):
        if isinstance(stmt, list):
            for statement in stmt:
                self.resolve(statement)
        else:
            stmt.accept(self)

    def resolve_local(self, expr, name):
        for i in range(len(self.scopes)):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

    def resolve_function(self,function, current_function_type):
        enclosing_function_type = self.current_function
        self.current_function = current_function_type
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()
        self.current_function = enclosing_function_type

    def begin_scope(self):
        self.scopes.append({})
    def end_scope(self):
        self.scopes.pop()