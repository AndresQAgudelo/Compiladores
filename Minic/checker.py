
# checker.py
#
# Este archivo tendrá la parte de verificación/validación de los tipo 
# de datos del compilador.  Hay una serie de cosas que deben gestionarse 
# para que esto funcione.  Primero, debe tener alguna noción de "tipo" 
# en su compilador.
# En segundo lugar, debe administrar entornos/ámbito para manejar los 
# nombres de las definiciones (variables, funciones, etc.).
#
# Una clave para esta parte del proyecto serán las pruebas adecuadas.  
# A medida que agrega código, piense en cómo podría probarlo.
#
# ---------------------------------------------------------------------
# Revisa diferentes aspectos del codigo:
#
# 1. Todos los IDENT deben de estar debidamente declarados, en su
#    respectivo contexto (env)
#
# 2. Revisar los tipos de datos
#    a. numeric : + - * / %
#    b. string  : + (concatenar)
#    c. boolean : ! || &&
#    d. void    : comparacion (==, !=)
#
# 3. Control de flujo
#    a. Debe de existir una funcion main
#    b. toda funcion debe de tener al menos un return
#    c. las instrucciones break/continue deben de estar
#       definidas dentro de un while/for
#
# ---------------------------------------------------------------------

from mcast import *

# ---------------------------------------------------------------------
#  Tabla de Simbolos
# ---------------------------------------------------------------------

class Symtab:
    '''
    Una tabla de símbolos.  Este es un objeto simple que sólo
    mantiene una hashtable (dict) de nombres de simbolos y los
    nodos de declaracion o definición de funciones a los que se
    refieren.
    Hay una tabla de simbolos separada para cada elemento de
    código que tiene su propio contexto (por ejemplo cada función,
    clase, tendra su propia tabla de simbolos). Como resultado,
    las tablas de simbolos se pueden anidar si los elementos de
    código estan anidados y las búsquedas de las tablas de
    simbolos se repetirán hacia arriba a través de los padres
    para representar las reglas de alcance léxico.
    '''
    class SymbolDefinedError(Exception):
        '''
        Se genera una excepción cuando el código intenta agregar
        un simbol a una tabla donde el simbol ya se ha definido.
        Tenga en cuenta que 'definido' se usa aquí en el sentido
        del lenguaje C, es decir, 'se ha asignado espacio para el
        simbol', en lugar de una declaración.
        '''
        pass
        
    def __init__(self, parent=None):
        '''
        Crea una tabla de símbolos vacia con la tabla de
        simbolos padre dada.
        '''
        self.entries = {}
        self.parent = parent
        if self.parent:
            self.parent.children.append(self)
        self.children = []
        
    def add(self, name, value):
        '''
        Agrega un simbol con el valor dado a la tabla de simbolos.
        El valor suele ser un nodo AST que representa la declaración
        o definición de una función, variable (por ejemplo, Declaración
        o FuncDeclaration)
        '''
        if name in self.entries:
            raise Symtab.SymbolDefinedError()
        self.entries[name] = value
        
    def get(self, name):
        '''
        Recupera el símbol con el nombre dado de la tabla de
        simbol, recorriendo hacia arriba a traves de las tablas
        de simbol principales si no se encuentra en la actual.
        '''
        if name in self.entries:
            return self.entries[name]
        elif self.parent:
            return self.parent.get(name)
        return None


class Checker(Visitor):
    '''
    Visitante que crea y enlaza tablas de simbolos al AST
    ''' 
    def _add_symbol(self, node, env: Symtab):
        '''
        Intenta agregar un símbolo para el nodo dado a
        la tabla de símbolos actual, capturando cualquier
        excepción que ocurra e imprimiendo errores si es
        necesario.
        '''
        try:
            env.add(node.name, node)
        except Symtab.SymbolDefinedError:
            self.error(f"Simbol '{node.name}' esta definido.")
            
    @classmethod
    def check(cls, node: TranslationUnit):
        checker = cls()
        node.accept(checker, Symtab())
        return checker
        
    # nodos de Declaration


    def visit(self, node: FunctionDefn, env: Symtab):
        '''
        1. Agregar el nombre de la función a la tabla de simbolos actual
        2. Crear una nueva tabla de simbolos (contexto)
        3. Agregamos los parametros a la nueva tabla de simbolos
        4. Visitar cada una de las instrucciones del cuerpo de la funcion
        '''
        self._add_symbol(node, env)         # 1
        env = Symtab(env)                   # 2
        node.params.accept(self, env)       # 3
        node.stmts.accept(self,env)         # 4


    def visit(self, node: ParamList, env: Symtab):
        '''
        1. Agregar cada uno de los Parameter a la tabla de simbolos
        '''
        for param in node.params:
            self._add_symbol(param)


    def visit(self, node: CompountStmt, env: Symtab):
        '''
        1. Crear una nueva tabla de simbolos (contexto)
        2. Agregamos las Declaration a la nueva tabla de simbolos
        3. Visitar cada una de las instrucciones del cuerpo de la funcion
        '''
        env = Symtab(env)                   # 1
        for decl in node.decls:
            decl.accept(self, env)
        for stmt in node.stmts:
            stmt.accept(self, env)


    def visit(self, node: VariableDefn, env: Symtab):
        '''
        1. Agregar el nombre de la variable a la tabla de simbolos actual
        2. Visitar la expresion, si esta definida 
        '''
        self._add_symbol(node, env)         # 1
        if node.expr:                       # 2
            node.expr.accept(self, env)
        
    # Statement
        
    def visit(self, node: If, env: Symtab):
        '''
        1. Visitar la condicion
        2. Visitar las instrucciones del then
        3. Visitar las instrucciones del opt, si esta definido
        '''
        node.test.accept(self, env)
        node.cons.accept(self, env)
        if node.altr:
            node.altr.accept(self, env)
        
    def visit(self, node: WhileStmt, env: Symtab):
        '''
        1. Visitar la condicion
        2. Visitar las instrucciones del cuerpo
        Nota : ¿Generar un nuevo contexto?
        '''
        node.test.accept(self, env)
        for stmt in node.body:
            stmt.accept(self, env)

    def visit(self, node: Return, env: Symtab):
        '''
        1. Visitar expresion
        '''
        node.expr.accept(self, env)
        
    def visit(self, node: ExprStmt, env: Symtab):
        '''
        1. Visitar expresion
        '''
        pass
        
        
    # Expression
    
    def visit(self, node: Literal, env: Symtab):
        '''
        No se hace nada
        '''
        pass
        
    def visit(self, node: Binary, env: Symtab):
        '''
        1. Visitar el hijo izquierdo
        2. Visitar el hijo derecho
        '''
        node.left.accept(self, env)
        node.right.accept(self, env)
        
    def visit(self, node: Logical, env: Symtab):
        '''
        1. Visitar el hijo izquierdo
        2. Visitar el hijo derecho
        '''
        node.left.accept(self, env)
        node.right.accept(self, env)
        
    def visit(self, node: Unary, env: Symtab):
        '''
        1. Visitar expresion
        '''
        pass
        
    def visit(self, node: Grouping, env: Symtab):
        '''
        1. Visita Expresion
        '''
        pass
        
    def visit(self, node: Variable, env: Symtab):
        '''
        1. Buscar nombre en la tabla de simbolos (contexto actual)
        '''
        value = env.get(node.name)
        if value is None:
            print(f'La Variable {node.name} no esta definida')
        
    def visit(self, node: Assign, env: Symtab):
        '''
        1. Visitar el hijo izquierdo (OJO)
        2. Visitar el hijo derecho
        '''
        node.name.accept(self, env)
        node.expr.accept(self, env)
        
    def visit(self, node: Call, env: Symtab):
        '''
        1. Buscar la funcion en la tabla de simbolos
        2. Validar el numero de argumentos y tipos pasados
        3. Visitar las expr de los argumentos
        '''
        pass