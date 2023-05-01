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

# ---------- DECLARATION -------------
        
    def visit(self, node : FuncDefinition):
        name = self.name()
        self.dot.node(name,
            label=f"FuncDefinition  \n type : {node.type} \n static : {node.static} \n extern : {node.extern}",
            )
        
        self.dot.edge(name, self.visit(node.name))
        print(node.params)
        self.dot.edge(name, self.visit(node.params) )
        print(node.stmts)
        self.dot.edge(name, self.visit(node.stmts))
        
        return name

    def visit(self, node : VarDefinition):
        name = self.name()
        self.dot.node(name,
            label=fr"VarDefinition\ntype:'{node.type}'\nextern: '{node.extern} \nstatic: '{node.static}'"
            )
        
        if node.expr:
            self.dot.edge(name, self.visit(node.expr))
        return name
    
    def visit(self, node: ParamList):
        name = self.name()
        self.dot.node(name,
            label=f"ParamList \n ellipsis : {node.ellipsis} ",
            )

        if node.params:
            for n in node.params:
                self.dot.edge(name, self.visit(n))
        
        return name

    def visit(self, node :Parameter):
        name = self.name()
        self.dot.node(name, label= f"Parameter \n type :{node.type}")
        self.dot.edge(name, self.visit(node.name))
        
        return name
    
    # -------- STATEMENT ---------------

    def visit(self, node : CompoundStmt):
        name = self.name()
        self.dot.node(name,
            label="CompountStmt",
            )
        if node.decl:
            for n in node.decl:
                self.dot.edge(name, self.visit(n), label= 'decl')
        
        if node.stmt:
            for n in node.stmt:
                self.dot.edge(name, self.visit(n), label= 'stmt')

        return name
        
    def visit(self, node:Assignment):
        name = self.name()
        self.dot.node(name, label=f"Assignment \n op : {node.op} ")
        self.dot.edge(name, node.loc.accept(self))
        self.dot.edge(name, node.expr.accept(self))
        return name

    def visit(self, node:Binary):
        name = self.name()
        self.dot.node(name, label=f"Binary \n op : {node.op} ")
        self.dot.edge(name, node.left.accept(self))
        self.dot.edge(name, node.right.accept(self))
        return name

    def visit(self, node: WhileLoop):
        name = self.name()
        self.dot.node(name, label=f"WhileLoop")

        if node.expr:
            self.dot.edge(name, self.visit(node.expr), label= 'expr')

        if node.stmt:
            self.dot.edge(name, self.visit(node.stmt), label= 'stmt')
        
        return name
    
    def visit(self, node: ForLoop):
        name = self.name()
        self.dot.node(name, label= "ForLoop")

        if node.begin:
            self.dot.edge(name, self.visit(node.begin), label= ' begin')
        
        if node.expr:
            self.dot.edge(name, self.visit(node.expr), label= ' expr')
        
        if node.end:
            self.dot.edge(name, self.visit(node.end), label= 'end')
        
        if node.stmt:
            self.dot.edge(name, self.visit(node.stmt), label= 'stmt')

        return name
    
    def visit(self, node: Continue):
        name = self.name()
        self.dot.node(name, label= "Continue")
        return name

    def visit(self, node: Break):
        name = self.name()
        self.dot.node(name, label= "Break")
        return name

    def visit(self, node: Return):
        name = self.name()
        self.dot.node(name, label= "Return")
        self.dot.edge(name, self.visit(node.expr))
        return name
        
    def visit(self, node: IfStmt):
        name = self.name()
        self.dot.node(name, label = "IfStmt")
        if node.cond:
            self.dot.edge(name, self.visit(node.cond), label='cond')
        if node.cons:
            self.dot.edge(name, self.visit(node.cons), label='cons')
        if node.altr:
            self.dot.edge(name, self.visit(node.altr), label='altr')
        return name

# ------- EXPRESIONN ----------------

    def visit(self, node:Integer):
        name = self.name()
        self.dot.node(name, label=f"Integer \n type :'{node.type}\n name :'{node.value}")
        return name

    def visit(self, node:Float):
        name = self.name()
        self.dot.node(name, label=f"Float \n type :'{node.type}\n name :'{node.value}")
        return name

    def visit(self, node:Char):
        name = self.name()
        self.dot.node(name, label=f"Char \n type :'{node.type}\n name :'{node.value}")
        return name

    def visit(self, node:String):
        name = self.name()
        self.dot.node(name, label=f"String \n type :'{node.type}\n name :'{node.value}")
        return name

    def visit(self, node:Ident):
        name = self.name()
        self.dot.node(name, label=f"Ident \n name :'{node.name}'")
        return name
    
    def visit(self, node:Pointer):
        name = self.name()
        self.dot.node(name, label=f"Pointer \n op : *")

        self.dot.edge(name,self.visit(node.expr) )
        return name

    def visit(self, node:Negative):
        name = self.name()
        self.dot.node(name, label=f"Negative \n op : -")

        self.dot.edge(name,self.visit(node.expr) )
        return name
    
    def visit(self, node:Unary):
        name = self.name()
        self.dot.node(name, label=f"Unary \n op : +")

        self.dot.edge(name,self.visit(node.expr) )
        return name

    def visit(self, node:Not):
        name = self.name()
        self.dot.node(name, label=f"Not \n op : !")

        self.dot.edge(name,self.visit(node.expr) )
        return name

    def visit(self, node:AddrOf):
        name = self.name()
        self.dot.node(name, label=f"Negative \n op : &")

        self.dot.edge(name,self.visit(node.expr) )
        return name

    def visit(self, node:Array):
        name = self.name()
        self.dot.node(name, label=f"Array")

        self.dot.edge(name,self.visit(node.expr) )
        self.dot.edge(name,self.visit(node.index) )
        return name

    def visit(self, node:Call):
        name = self.name()
        self.dot.node(name, label=f"Call")

        self.dot.edge(name,self.visit(node.func), label="func" )
        
        self.dot.edge(name,self.visit(node.arglist))
        return name


    
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
    