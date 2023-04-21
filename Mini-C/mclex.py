# mclex.py
r'''
El papel de un analizador léxico es convertir texto sin procesar en símbolos 
reconocidos conocidos como tokens.

Se requiere que el analizador léxico de MiniC reconozca los siguientes 
símbolos. El nombre sugerido del token está a la izquierda. El texto 
coincidente está a la derecha.


Palabras Reservadas:
    STATIC  : 'static'
    EXTERN  : 'extern'
    INT     : 'int'
    FLOAT   : 'float'
    CHAR    : 'char'
    CONST   : 'const'
    RETURN  : 'return'
    BREAK   : 'break'
    CONTINUE: 'continue'
    IF      : 'if'
    ELSE    : 'else'
    WHILE   : 'while'
    ...

Identificadores:
    ID      : Texto iniciando con una letra o '_' seguido de cualquier 
              número de letras, digitos o '_'. 
              Ejemplo: 'abc' 'ABC' 'abc123' '_abc' 'a_b_c'

Literales:
    INUMBER : 123 (decimal)

    FNUMBER : 1.234
              .1234
              1234.

    CHARACTER:'a' (un solo caracter - byte)
              '\xhh' (valor byte)
              '\n' (newline)
              '\'' (literal comilla simple)

    STRING  : "cadena" (varios caracteres entre comilla doble)
              permite secuenciads de escape como: '\n', '\t\, etc..

Operadores:
    PLUS    : '+'
    MINUS   : '-'
    TIMES   : '*'
    DIVIDE  : '/'
    LT      : '<'
    LE      : '<='
    GT      : '>'
    GE      : '>='
    EQ      : '=='
    NE      : '!='
    LAND    : '&&'
    LOR     : '||'
    LNOT    : '!'

Simbolos Miselaneos
    ASSIGN  : '='
    ADDEQ   : '+='
    SUBEQ   : '-='
    MULEQ   : '*='
    DIVEQ   : '/='
    MODEQ   : '%='
    SEMI    : ';'
    LPAREN  : '('
    RPAREN  : ')'
    LBRACE  : '{'
    RBRACE  : '}'
    COMMA   : ','
    ELLIPSIS: '...'

Comentarios: Deben ser ignorados
    //          Ignora el resto de la linea
    /* ... */   Ignora un bloque (no se permite anidar)

Errores: Su lexer puede opcionalmente reconocer e informar los siguientes 
mensajes de error:

    lineno: character 'c' ilegal
    lineno: constante de caracter no terminada
    lineno: comentario sin terminar

'''
import sly

class Lexer(sly.Lexer):
    tokens = {
        # Palabras Reservadas
        BREAK, CHAR, CONST, CONTINUE, ELSE, EXTERN, FLOAT,
        FOR, IF, INT, RETURN, STATIC, VOID, WHILE,

        # Operadores
        LE, GE, EQ, NE, LAND, LOR,
        ADDEQ, SUBEQ, MULEQ, DIVEQ, MODEQ,

        # Tokens complejos
        ID, INUMBER, FNUMBER, CHARACTER, STRING, ELLIPSIS,
    }
    literals = '+-*/%=<>!&(){}[]:;,.'

    # Ignorar espacios en blanco (white-spaces)
    ignore = ' \t\r'

    # Operadores de relacion
    LE = r'<='
    GE = r'>='
    EQ = r'=='
    NE = r'!='

    # Operadores logicos
    LOR  = r'\|\|'
    LAND = r'&&'

    ADDEQ = r'\+='
    SUBEQ = r'-='
    MULEQ = r'\*='
    DIVEQ = r'/='
    MODEQ = r'%='

    # Identificador
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'

    # Casos Especiales (Palabras Reservadas)
    ID['break']    = BREAK 
    ID['char']     = CHAR 
    ID['const']    = CONST 
    ID['continue'] = CONTINUE 
    ID['else']     = ELSE 
    ID['extern']   = EXTERN 
    ID['float']    = FLOAT 
    ID['for']      = FOR 
    ID['if']       = IF
    ID['int']      = INT
    ID['return']   = RETURN 
    ID['static']   = STATIC 
    ID['void']     = VOID
    ID['while']    = WHILE

    ELLIPSIS = r'\.\.\.'

    # literals
    CHARACTER = r"'\w'"

    @_(r'[0-9]+')
    def INUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r'[0-9]*\.[0-9]+|[0-9]+\.[0-9]*')
    def FNUMBER(self, t):
        t.value = float(t.value)
        return t

    STRING = r'".*"'

    @_(r'/\*(.|\n)*\*/')
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')

    @_(r'//.*\n')
    def ignore_cppcomment(self, t):
        self.lineno += 1

    # Ignorar newline
    @_('\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print(f"[red]{self.lineno}: Caracter '{t.value[0]}' es ilegal[/red]")
        self.index += 1

def pprint(source):
    from rich.table   import Table
    from rich.console import Console

    lex = Lexer()

    table = Table(title='Analizador Léxico')
    table.add_column('token')
    table.add_column('value')
    table.add_column('lineno', justify='right')

    for tok in lex.tokenize(source):
        value = tok.value if isinstance(tok.value, str) else str(tok.value)
        table.add_row(tok.type, value, str(tok.lineno))
    
    console = Console()
    console.print(table, justify='center')

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print(f"usage: python {sys.argv[0]} fname")
        exit(1)

    pprint(open(sys.argv[1], encoding='utf-8').read())    