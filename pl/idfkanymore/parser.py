import lark

s = open("lang.idk", "r").read()

parser = lark.Lark.open("lang.lark", start="start", parser="lalr")
tree = parser.parse(s)
print(tree.pretty())
