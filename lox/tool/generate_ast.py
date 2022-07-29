import sys
def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: generate_ast <output directory>")
        sys.exit(1)
    output_dir = sys.argv[1]
    define_ast(output_dir, "Expr", [
      "Binary   : Expr left, Token operator, Expr right",
      "Grouping : Expr expression",
      "Literal  : Object value",
      "Unary    : Token operator, Expr right"
    ])
    define_ast(output_dir, "Stmt", [
      "Expression   : Expr expression",
      "Print        : Expr expression"
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
    fields = list(map(lambda s: s.split()[1],field_list.split(',')))
    print(f"\tdef __init__(self,{','.join(fields)}):", file=file)
    for field in fields:
        print(f"\t\tself.{field} = {field}", file=file)
    print("", file=file)
    print("\tdef accept(self, visitor):", file=file)
    print(f"\t\treturn visitor.visit{class_name}{base_name}(self)",file=file)

if __name__ == "__main__":
    main()

