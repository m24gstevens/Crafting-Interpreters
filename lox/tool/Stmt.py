from pylox import *
class Stmt:
	pass

class Visitor:
	pass
class Block(Stmt):
	def __init__(self,statements):
		self.statements = statements

	def accept(self, visitor):
		return visitor.visitBlockStmt(self)

class Break(Stmt):
	def __init__(self):
		pass

	def accept(self, visitor):
		return visitor.visitBreakStmt(self)

class Expression(Stmt):
	def __init__(self,expression):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visitExpressionStmt(self)

class Function(Stmt):
	def __init__(self,name,function):
		self.name = name
		self.function = function

	def accept(self, visitor):
		return visitor.visitFunctionStmt(self)

class If(Stmt):
	def __init__(self,condition,then_branch,else_branch):
		self.condition = condition
		self.then_branch = then_branch
		self.else_branch = else_branch

	def accept(self, visitor):
		return visitor.visitIfStmt(self)

class Print(Stmt):
	def __init__(self,expression):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visitPrintStmt(self)

class Return(Stmt):
	def __init__(self,keyword,value):
		self.keyword = keyword
		self.value = value

	def accept(self, visitor):
		return visitor.visitReturnStmt(self)

class Var(Stmt):
	def __init__(self,name,initializer):
		self.name = name
		self.initializer = initializer

	def accept(self, visitor):
		return visitor.visitVarStmt(self)

class While(Stmt):
	def __init__(self,condition,body):
		self.condition = condition
		self.body = body

	def accept(self, visitor):
		return visitor.visitWhileStmt(self)

