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
            print(n)
            self.dot.edge(name, self.visit(n))
            
        return name
    
    def visit(self, node : FuncDefinition):
        name = self.name()
        self.dot.node(name,
            label=f"FuncDefinition \n name : {node.name} \n type : {node.type} \n static : {node.static} \n extern : {node.extern}",
            )
        
        print(node.params)
        self.dot.edge(name, self.visit(node.params))
        print(node.stmts)
        self.dot.edge(name, self.visit(node.stmts))
        
        return name
    
    def visit(self, node: ParamList):
        name = self.name()
        self.dot.node(name,
            label=f"ParamList \n ellipsis : {node.ellipsis} ",
            )

        for n in node.params:
            print(n)
            self.dot.edge(name, self.visit(n))
        
        return name

    def visit(self, node :Parameter):
        name = self.name()
        self.dot.node(name, label= "Parameter")
        
        return name

    def visit(self, node : CompoundStmt):
        name = self.name()
        self.dot.node(name,
            label="CompountStmt",
            )
        if node.decl:
            for n in node.decl:
                print(n)
                self.dot.edge(name, self.visit(n))

        return name
    
    def visit(self, node : VarDefinition):
        name = self.name()
        self.dot.node(name,
            label=fr"VarDefinition\ntype:'{node.type}'\nextern: '{node.extern}'"
            )
        
        #if node.expr:
            #self.dot.edge(name, self.visit(node.expr))
        return name
    
    def visit(self, node : Ident):
        name = self.name()
        self.dot.name(name, label= "Ident")
        return name
    def visit(self, node:Assignment):
        name = self.name()
        self.dot.node(name, label=f"Assignment\\n {node.op} ")
        self.dot.edge(name, node.left.accept(self))
        self.dot.edge(name, node.right.accept(self))
        return name

    def visit(self, node:Binary):
        name = self.name()
        self.dot.node(name, label=f"Binary\\n {node.op} ")
        self.dot.edge(name, node.left.accept(self))
        self.dot.edge(name, node.right.accept(self))
        return name
    

    
        
    '''    

    def visit(self, node:Variable):
        name = self.name()
        self.dot.node(name, label=f"Variable\\nname='{node.name}'")
        return name
    

    

    
    def visit(self, node : VarDefinition):
        name = self.name()
        self.dot.node(name,
            label=fr"VarDefinition\ntype:'{node.type}'\nextern: '{node.extern}'"
            )
        
        if node.expr:
            self.dot.edge(name, self.visit(node.expr))
        return name


    def visit(self, node:Integer):
        name = self.name()
        self.dot.node(name, label=f"Literal\\nname='{node.value}")
        return name
    
    

    
    def visit(self, n:Unary):
        name = self.name()
        self.dot.node(name, label=f"Unary\\nop='{n.op}")
        self.dot.edge(name, n.expr.accept(self))
        return name
    
''''''

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
    dot.save("AST.dot")
    