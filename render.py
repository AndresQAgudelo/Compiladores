from mcast import *
import graphviz as gpv

from mclex import *
from mcparse import *
from rich import print

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
        self.dot = gpv.Digraph('AST', comment='AST')
        self.dot.attr('node', **self.node_default)
        self.dot.attr('edge', **self.edge_default)
        self.seq = 0
    
    def __repr__(self):
        return self.dot.source

    def __str__(self):
        return self.dot.source
    
    def name(self):
        self.seq += 1
        return f'n{self.seq:02d}'

    @classmethod
    def render(cls, n:Node):
        dot = cls()
        n.accept(dot)
        return dot.dot
    
 
    def visit(self, node : TranslationUnit):
        name = self.name()
        self.dot.node(name,
            label="TranslationUnit\\n"
            )
        for n in node.decl:
            self.dot.edge(name, self.visit(n))
        return name
    
    def visit(self, node : FuncDefinition):
        name = self.name()
        self.dot.node(name,
            label=fr"FuncDefinition\nname:'{node.name}'\ntype: {node.type}\nstatic: {node.static}\n params : {node.params}",
            )
        for n in node.stmts:
            print(n)
            self.dot.edge(name, self.visit(n))
            
        return name
    
    def visit(self, node : VarDefinition):
        name = self.name()
        self.dot.node(name,
            label=fr"VarDefinition\ntype:'{node.type}'\nextern: '{node.extern}'"
            )
        
        self.dot.edge(name, self.visit(node.expr))
        return name

    def visit(self, node:Variable):
        name = self.name()
        self.dot.node(name, label=f"Variable\\nname='{node.name}'")
        return name

    def visit(self, node:ExprStmt):
        name = self.name()
        self.dot.node(name,
            label='ExprStmt',
            color=self.color)
        print(node.expr)
        for n in node.expr:
            self.dot.edge(name, self.visit(n))
        return name

    def visit(self, node:Literal):
        name = self.name()
        self.dot.node(name, label=f"Literal\\nname='{node.value}")
        return name

    def visit(self, n:Binary):
        name = self.name()
        self.dot.node(name, label="Binary\\nAssignment")
        #self.dot.edge(name, n.left.accept(self))
        #self.dot.edge(name, n.right.accept(self))
        return name
    
        
'''   def visit(self, n:Binary):
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


    
    def visit(self, n:Literal):
        name = self.name()
        self.dot.node(name, label=f"Literal\\nname='{n.value}")
        return name
    
    # DECLARACIONES
    '''



if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 2:
        print(f"usage: python {sys.argv[0]} [ fname1 [ fname2 ... ] ]   --ast")
        exit(1)
    

    l = Lexer()
    p = Parser()
    
    data = open(sys.argv[1], encoding='utf-8').read()

    ast = p.parse(l.tokenize(data))
    dot = RenderAST.render(ast)
    #dot = RenderAST()
    #ast.accept(dot)

    print(dot)
    