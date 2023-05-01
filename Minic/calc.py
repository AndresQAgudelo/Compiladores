# calc.py
'''
expr := expr '+' term
      | expr '-' term
      | term
      ;

term := term '*' factor
      | term '/' factor
      | term '%' factor
      | factor
      ;

factor := NUMBER
      | '-' factor
      | '(' expr ')'
      ;
'''
from dataclasses import dataclass
from multimethod import multimeta
from rich import print
import graphviz as gpv
import sly

# ---- Clases Abstractas

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
   op  : str
   expr: Expression


@dataclass
class Number(Expression):
   value: int

# --- Render AST

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
       self.dot.node(name, label=f"Binary='{n.op}'")
       self.dot.edge(name, n.left.accept(self))
       self.dot.edge(name, n.right.accept(self))
       return name

    def visit(self, n:Unary):
       name = self.name()
       self.dot.node(name, label=f"Unary='{n.op}'")
       self.dot.edge(name, n.expr.accept(self))
       return name

    def visit(self, n:Number):
       name = self.name()
       self.dot.node(name, label=f"Number\\nvalue='{n.value}'")
       return name


# ---- Calculadora

class Calculate(Visitor):
   @classmethod
   def calc(cls, n:Node):
      calc = cls()
      return n.accept(calc)

   def visit(self, n:Binary):
      left  = n.left.accept(self)
      right = n.right.accept(self)
      if n.op == '+':
         return left + right
      elif n.op == '-':
         return left - right
      elif n.op == '*':
         return left * right
      elif n.op == '/':
         return left / right
      elif n.op == '%':
         return left % right

   def visit(self, n:Unary):
      return - n.expr.accept(self)

   def visit(self, n:Number):
      return n.value





class Lexer(sly.Lexer):
    tokens = {
        NUMBER,
    }
    literals = '+-*/%()'

    ignore = ' \t\r'

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    def error(self, t):
        print(f"Linea {self.lineno}: [red]El caracter [blink]'{t.value[0]}'[/blink] NO es permitido[/red]")
        self.index += 1


class Parser(sly.Parser):
    debugfile='calc.txt'

    tokens = Lexer.tokens

    @_("expr '+' term", 
       "expr '-' term")
    def expr(self, p):
      return Binary(p[1], p.expr, p.term)

    @_("term")
    def expr(self, p):
      return p.term

    @_("term '*' factor",
       "term '/' factor",
       "term '%' factor")
    def term(self, p):
      return Binary(p[1], p.term, p.factor)

    @_("factor")
    def term(self, p):
      return p.factor

    @_("NUMBER")
    def factor(self, p):
      return Number(p.NUMBER)

    @_("'-' factor")
    def factor(self, p):
      return Unary(p[0], p.factor)

    @_("'(' expr ')'")
    def factor(self, p):
      return p.expr

    def error(self, p):
        if p:
            print("Syntax error at token", p.type)
            # Just discard the token and tell the parser it's okay.
            self.errok()
        else:
            print("Syntax error at EOF")



# --- Mis pruebas

d = '1 + 2 * 3 - 4 - (17 / 45)'
l = Lexer()
p = Parser()

ast = p.parse(l.tokenize(d))
print(ast)
dot = RenderAST.render(ast)

print(f"{d} = {Calculate.calc(ast)}")