# mcast.py
'''
Este archivo define un modelo de datos para los programas MiniC.

Básicamente, el modelo es una gran estructura de datos que representa
el contenido de un programa como objetos, no como texto.  A veces, 
esta estructura se conoce como "árbol de sintaxis abstracta" o AST.
Sin embargo, no está necesariamente ligado directamente a la sintaxis 
real del lenguaje.  Por lo tanto, preferimos pensar en ello como un 
modelo de datos más genérico.

Para hacer esto, necesita identificar los diferentes "elementos" que 
componen un programa y codificarlos en clases.  Para hacer esto, puede 
ser útil "pensar poco" el problema.  Para ilustrar, suponga que desea 
codificar la idea de "asignar un valor".  La asignación implica una 
ubicación (el lado izquierdo) y un valor como este:

	location = expression;

Para representar esto, haz una clase con solo esas partes:

	@dataclass
	class Assignment:
		location: Expression
		expr    : Expression

Ahora bien, ¿qué son "location" y "expr"?  ¿Importa?  Tal vez no.  
Todo lo que sabe es que un operador de asignación requiere ambas 
partes.  NO LO PIENSE DEMASIADO.  Se irán completando más detalles 
a medida que evolucione el proyecto.

Este archivo está dividido en secciones que describen parte de la 
especificación del lenguaje MiniC en los comentarios.  Deberá adaptar
esto al código real.

Comenzando, recomendaría no hacer este archivo demasiado elegante.  
Simplemente use definiciones de clases básicas de Python.  Puede 
agregar mejoras de usabilidad más adelante.
'''
from dataclasses import dataclass, field
from multimethod import multimeta
from typing      import List


# ----------------------------------------------------------------------
# Clases Abstractas
# ----------------------------------------------------------------------
@dataclass
class Visitor(metaclass=multimeta):
    pass


@dataclass
class Node:
    '''
    Representa cualquier nodo del AST
    '''
    def accept(self, v:Visitor, *args, **kwargs):
        return v.visit(self, *args, **kwargs)


@dataclass
class Statement(Node):
    '''
    '''
    pass


@dataclass
class Expression(Node):
    '''
    '''
    pass


@dataclass
class Declaration(Statement):
    '''
    Declaraciones de funciones/variables/constantes
    '''
    pass


# ----------------------------------------------------------------------
# Clases Concretas
# ----------------------------------------------------------------------

# Statements

@dataclass
class TranslationUnit(Statement):
    decl: List[Declaration]


@dataclass
class CompountStmt(Statement):
    decls : List[Declaration]=field(default_factory=list)
    stmts : List[Statement] = field(default_factory=list)

# Instrucciones

@dataclass
class WhileLoop(Statement):
    expr : Expression
    stmt : Statement


@dataclass
class ForLoop(Statement):
    begin : Statement
    expr  : Expression
    end   : Statement
    stmt  : Statement


@dataclass
class Continue(Statement):
    pass

# Declaraciones

@dataclass
class Parameter(Declaration):
    type : str
    name : str

@dataclass
class ParamList(Declaration):
    params  : List[Parameter]=field(default_factory=list)
    ellipsis: bool = False

@dataclass
class FunctionDefn(Declaration):
    type  : str 
    name  : str
    params: ParamList=field(default_factory=list)
    stmts : CompountStmt=field(default_factory=list)
    static: bool = False
    extern: bool = False

@dataclass
class VariableDefn(Declaration):
    type  : str
    name  : str
    expr  : Expression = None
    static: bool = False
    extern: bool = False

# Expresiones

@dataclass
class Binary(Expression):
    op   : str 
    left : Expression
    right: Expression

@dataclass
class Unary(Expression):
    op   : str 
    expr : Expression
