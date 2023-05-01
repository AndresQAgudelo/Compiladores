# checker.py
#
# Este archivo tendrá la parte de verificación/validación de tipo de datos del compilador.  
# Hay una serie de cosas que deben gestionarse para que esto funcione.  Primero, debe 
# tener alguna noción de "tipo" en su compilador.
#
# En segundo lugar, debe administrar entornos/ámbito para manejar los nombres de las 
# definiciones (variables, funciones, etc.).
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

    In_Loop = False
    iteracion_actual = 0
    condicion_parada = 0
    def _add_symbol(self, node, env: Symtab):
        '''
        Intenta agregar un símbolo para el nodo dado a
        la tabla de símbolos actual, capturando cualquier
        excepción que ocurra e imprimiendo errores si es
        necesario.
        '''
        try:
            self.curr_symtab.add(node.name, node)
        except Symtab.SymbolDefinedError:
            self.error(f"Simbol '{node.name}' esta definido.")
            
    @classmethod
    def check(cls, model):
        checker = cls()
        model.accept(checker, Symtab())
        return checker

    # ---- Declaration ------
    
    def visit(self, node: FuncDefinition, env: Symtab):
        '''
        1. Agregar el nombre de la función a la tabla de simbolos actual
        2. Crear una nueva tabla de simbolos (contexto)
        3. Agregamos los parametros a la nueva tabla de simbolos
        4. Visitar cada una de las instrucciones del cuerpo de la funcion
        '''
        self._add_symbol(node, env)
        env = Symtab(env)

        for param in node.params:
            self._add_symbol(VarDefinition(param))
        for stmt in node.stmts:
            stmt.accept(self, env)
        
    def visit(self, node: VarDefinition, env: Symtab):
        '''
        1. Agregar el nombre de la variable a la tabla de simbolos actual
        2. Visitar la expresion, si esta definida
        '''
        self._add_symbol(node, env)
        if node.expr:
            node.expr.accept(self, env)
    
    def visit(self, node: ParamList , env: Symtab):
        '''
        1. Agregar el nombre de la variable a la tabla de simbolos actual
        2. Visitar la expresion, si esta definida
        '''

        self._add_symbol(node, env)
        if node.params:
            for params in node.params:
                params.accept(self, env)
    
    def visit(self, node: Parameter , env: Symtab):
        self.visit(node.name)
        

    # Statement
    
    def visit(self, node: CompoundStmt, env: Symtab):
        '''
        1. Visitar cada una de las instrucciones
        '''
        self._add_symbol(node, env)
        if node.decl:
            for decl in node.decl:
                decl.accept(self, env)
        if node.stmt:
            for stmt in node.stmt:
                stmt.accept(self, env)

    def visit(self, node: Assignment, env: Symtab):
        '''
        1. Visitar el hijo izquierdo
        2. Visitar el hijo derecho
        '''
        self.visit(node.loc, env)
        self.visit(node.expr, env)

    def visit(self, node: Binary, env: Symtab):
        '''
        1. Visitar el hijo izquierdo
        2. Visitar el hijo derecho
        '''
        self.visit(node.left, env)
        self.visit(node.right, env)

    def visit(self, node: Continue, env: Symtab):
        '''verificar que este drento del loop'''
        if not self.In_Loop == True:
            self.error(node, f"Checker error, continue not inside loop")

    def visit(self, node: Break, env: Symtab):
        '''verificar que este drento del loop'''
        if not self.In_Loop == True:
            self.error(node, f"Checker error, break not inside loop")

    def visit(self, node: IfStmt, env: Symtab):
        '''
        1. Visitar la condicion
        2. Visitar las instrucciones 
        3. Visitar las instrucciones del altr, si esta definido
        '''

        self.visit(node.cond, env)
        env = Symtab(env)
        self.visit(node.cons, env)
        if node.altr:
            self.visit(node.altr, env)

    def visit(self, node: WhileLoop, env: Symtab):
        '''
        1. Visitar la condicion
        2. Visitar las instrucciones del cuerpo
        Nota : ¿Generar un nuevo contexto?
        '''
        self.In_Loop = True #poner en true para que continue y break funcionen
        self.visit(node.expr, env)
        env = Symtab(env) #?????
        self.visit(node.stmt, env)
        self.In_Loop = False #cuando acaba el bucle, poner en false

    def visit(self, node: ForLoop, env: Symtab):
        self.In_Loop = True
        self.visit(node.begin, env) 
        self.visit(node.expr, env)
        self.visit(node.end, env)
        self.visit(node.stmt, env)
        self.In_Loop = False

    def visit(self, node: Return, env: Symtab):
        '''
        1. Visitar expresion
        '''
        if node.expr:
            self.visit(node.expr, env)
    
    def visit(self, node: Literal, env: Symtab):
        '''
        pass
        '''
        pass

    def visit(self, node: Unary, env: Symtab):
        '''
        1. Visitar expresion
        '''
        self.visit(node.expr, env)

    def visit(self, node: Ident, env: Symtab):
        '''
        1. Buscar nombre en la tabla de simbolos (contexto actual)
        '''
        result = env.get(node.name)
        if result is None:
            self.error(node, f"Checker error, the identifier '{node.name}' is not defined")

    def visit(self, node: Call, env: Symtab):
        '''
        1. Buscar la funcion en la tabla de simbolos
        2. Validar el numero de argumentos pasados
        3. Visitar las expr de los argumentos
        '''

        self.visit(node.func, env)
        result = env.get(node.func.name)
        if node.args is not None:
            for arg in node.args:
                self.visit(arg, env)

        if result is FuncDefinition:
            if result is not None:
                if result.parameters is not None:
                    if len(result.parameters)!=len(node.args):
                        self.error(node, "Checker error, given arguments don't match expected arguments in Call")

   