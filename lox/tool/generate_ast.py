import sys
def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: generate_ast <output directory>")
        sys.exit(1)
    output_dir = sys.argv[1]
    define_ast(output_dir, "Expr", [
      "Assign   : Token name, Expr value",
      "Binary   : Expr left, Token operator, Expr right",
      "Call     : Expr callee, Token paren, list arguments",
      "Get      : Expr object, Token name",
      "Set      : Expr object, Token name, Expr value",
      "This     : Token keyword",
      "Grouping : Expr expression",
      "Literal  : Object value",
      "Logical  : Expr left, Token operator, Expr right",
      "Unary    : Token operator, Expr right",
      "Variable : Token name",
      "FunctionExpression : list params, list body"
    ])
    define_ast(output_dir, "Stmt", [
      "Block        : list statements",
      "Class        : Token name, list methods",
      "Break        : ",
      "Expression   : Expr expression",
      "Function     : Token name, function function",
      "If           : Expr condition, Stmt then_branch, Stmt else_branch",
      "Print        : Expr expression",
      "Return       : Token keyword, Expr value",
      "Var          : Token name, Expr initializer",
      "While        : Expr condition, Stmt body"
    ])

def define_ast(output_dir, base_name, types):
    path = base_name + ".py"
    with open(path, "w") as f:
        print("from pylox import *", file=f)
        print(f"class {base_name}:", file=f)
        print("\tpass", file=f)
        print("", file=f)
        # Visitor pattern
        print(f"class Visitor:", file=f)
        print("\tpass", file=f)
        # Typr subsclasses
        for type in types:
            class_name = type.split(":")[0].strip()
            fields = type.split(":")[1].strip()
            define_type(f, base_name, class_name, fields)
            print("", file=f)

def define_type(file, base_name, class_name, field_list):
    print(f"class {class_name}({base_name}):", file=file)
    if field_list == "":
        fields = []
    else:
        fields = list(map(lambda s: s.split()[1],field_list.split(',')))
    print(f"\tdef __init__(self,{','.join(fields)}):", file=file)
    for field in fields:
        print(f"\t\tself.{field} = {field}", file=file)
    if len(fields) == 0:
        print("\tpass", file=file)
    print("", file=file)
    print("\tdef accept(self, visitor):", file=file)
    print(f"\t\treturn visitor.visit{class_name}{base_name}(self)",file=file)

if __name__ == "__main__":
    main()

