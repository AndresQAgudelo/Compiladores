# toy.py
import graphviz as gpv
import sly
from dataclasses import dataclass
from multimethod import multimeta
from rich import print


# ---- ESTRUCTURA DEL AST
@dataclass
class Visitor(metaclass=multimeta):
    pass


@dataclass
class Node:
    def accept(self, v:Visitor, *args, **kwargs):
        return v.visit(self, *args, **kwargs)


@dataclass
class Expression(Node):
    pass


@dataclass
class Binary(Expression):
    op   : str 
    left : Expression
    right: Expression


@dataclass
class Unary(Expression):
    op   : str 
    expr : Expression


@dataclass
class Id(Expression):
    name : str


# ---- VISITOR PARA IMPRIMIR AST
class RenderAST(Visitor):
    node_default = {
        'shape' : 'box',
        'color' : 'deepskyblue',
        'style' : 'filled',
    }
    edge_default = {
        'arrowhead' : 'none'
    }

    def __init__(self):
        self.dot = gpv.Digraph('AST', comment='Hola Clase')
        self.dot.attr('node', **self.node_default)
        self.dot.attr('edge', **self.edge_default)
        self.seq = 0
    
    def name(self):
        self.seq += 1
        return f'n{self.seq:02d}'

    @classmethod
    def render(cls, n:Node):
        dot = cls()
        n.accept(dot)
        return dot.dot

    def visit(self, n:Binary):
        name = self.name()
        self.dot.node(name, label="Binary\\nAssignment")
        self.dot.edge(name, n.left.accept(self))
        self.dot.edge(name, n.right.accept(self))
        return name

    def visit(self, n:Unary):
        name = self.name()
        self.dot.node(name, label=f"Unary\\nop='{n.op}")
        self.dot.edge(name, n.expr.accept(self))
        return name

    def visit(self, n:Id):
        name = self.name()
        self.dot.node(name, label=f"Ident\\nname='{n.name}")
        return name


# ---- ANALIZADOR LEXICO
class Lexer(sly.Lexer):
    tokens = {
        X,
    }
    literals = '*='

    ignore = ' \t\r'

    X = r'[a-zA-Z_]\w*'

    def error(self, t):
        print(f"[red]{self.lineno}: El caracter '{t.value[0]}' [blind]NO[/blind] es permitido[/red]")
        self.index += 1


# ---- ANALIZADOR SINTACTIVO
class Parser(sly.Parser):
    debugfile = 'toy.txt'

    tokens = Lexer.tokens

    @_("v '=' e")
    def s(self, p):
        return Binary(p[1], p.v, p.e)

    @_("e")
    def s(self, p):
        return p.e

    @_("v")
    def e(self, p):
        return p.v

    @_("X")
    def v(self, p):
        return Id(p.X)

    @_("'*' e")
    def v(self, p):
        return Unary(p[0], p.e)

    def error(self, p):
        print("[red]Error de Sintaxis[/red]")
        self.errok()

# ---- MAIN

data = 'a = *c'

l = Lexer()
p = Parser()

ast = p.parse(l.tokenize(data))
dot = RenderAST.render(ast)
#dot = RenderAST()
#ast.accept(dot)

print(dot)
