from pylox import *
class Stmt:
	pass

class Visitor:
	pass

class Expression(Stmt):
	def __init__(self,expression):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visitExpressionStmt(self)

class Print(Stmt):
	def __init__(self,expression):
		self.expression = expression

	def accept(self, visitor):
		return visitor.visitPrintStmt(self)

