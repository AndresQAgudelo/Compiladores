#mclexer.py
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
    CHAR    : 'CHAR'
    FOR     : 'for'

    CONST   : 'const'
    RETURN  : 'return'
    BREAK   : 'break'
    CONTINUE: 'continue'
    IF      : 'if'
    ELSE    : 'else'
    WHILE   : 'while'
    TRUE    : 'true'
    FALSE   : 'false'
    
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
    GT      : '!
    GE      : '>='
    EQ      : '=='
    NE      : '!='
    LAND    : '&&'
    LOR     : '||'
    LNOT    : '!'

Simbolos Miselaneos
    ASSIGN  : '='
    SEMI    : ';'
    LPAREN  : '('
    RPAREN  : ')'
    LBRACE  : '{'
    RBRACE  : '}'
    COMMA   : ','
    ASTERISK: '*'
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
# Definición Analizador Léxico
class Lexer(sly.Lexer):
        
    # Definición de Símbolos
    tokens = {
        # Palabras reservadas
        STATIC, EXTERN, INT, FLOAT, CHAR, CONST, RETURN, BREAK, CONTINUE, IF,
        ELSE, WHILE, TRUE, FALSE, FOR,

        # Identificadores
        ID,

        # Literales
        INUMBER, FNUMBER, CHARACTER, STRING,
        
        #Operadores
        PLUS, MINUS, TIMES,DIVIDE, LT, LE, GT, GE, EQ, NE, LAND, LOR, LNOT,
        
        #Simbolos miselaneaos
	ASSING, SEMI, LPAREN, RPAREN, LBRACE, RBRACE, COMMA, ASTERISK, ELLIPSE
	}
    
    literals = '+-*/%=(){}[];,' # Caracteres especiales 
    
    # Ignoramos espacios en blanco (white-space)
    ignore = ' \t\r'

    # Ignoramos newline
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    # Ignorar Comentarios de varias líneas
    @_(r'/\*(.|\n)*\*/')
    def ignore_comments(self, t):
        self.lineno += t.value.count('\n')

    # Ignorar Comentarios de una sola línea
    @_(r'//.*\n')
    def ignore_cppcomments(self, t):
        self.lineno += 1
    
    #Identificadores    
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['static'] = STATIC
    ID['extern'] = EXTERN
    ID['int'] = INT
    ID['float'] = FLOAT
    ID['char'] = CHAR
    ID['for'] = FOR
    ID['const'] = CONST
    ID['return'] = RETURN
    ID['break'] = BREAK
    ID['continue'] = CONTINUE
    ID['if'] = IF
    ID['else'] = ELSE
    ID['while'] = WHILE
    ID['true'] = TRUE
    ID['false'] = FALSE
    
    # Literales. Definición de Tokens a traves de funciones
    @_(r'".*"')
    def STRING(self, t):
        t.value = str(t.value)
        return t

    @_(r'(\d+\.\d*)|(\.\d+)')
    def FNUMBER(self, t):
        t.value = float(t.value)
        return t

    @_(r'\d+')
    def INUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r"'\w'")
    def CHARACTER(self, t):
        t.value = str(t.value)
        return t

    #Operadores
    PLUS = r'\+' # \ se usa para escapar caracteres especiales
    MINUS =r'-'
    TIMES =r'\*'
    DIVIDE =r'/'
    LT  = r'<'
    LE  = r'<='
    GT  = r'>'
    GE  = r'>='
    EQ  = r'=='
    NE  = r'!='
    LAND = r'&&'
    LOR  = r'\|\|'
    LNOT = r'!'
    
    #Miselaneus
    ASSING=r'='
    SEMI =r';'
    LPAREN =r'\('
    RPAREN =r'\)'
    RBRACE =r'}'
    LBRACE =r'{'
    COMMA =r','
    ASTERISK = r'\*'
    ELLIPSE = r'...'
    
    def find_column(text, token):
        last_cr = text.rfind('\n', 0, token.index)
        if last_cr < 0:
            last_cr = 0
        column = (token.index - last_cr) + 1
        return column
        
    # Error handling rule
    def error(self, t):
    	print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
    	self.index += 1
       

def pprint(source):
    from rich.table import Table
    from rich.console import Console
    from rich import box
    
    
    lex = Lexer()
    table = Table(title = 'Analizador Lexico', box = box.ASCII_DOUBLE_HEAD)
    table.add_column('type', justify="right", style="cyan", no_wrap=True)
    table.add_column('value', style="magenta")
    table.add_column('lineno', justify ="right", style="green")
 
    
    for tok in lex.tokenize(source):
    	value = tok.value if isinstance(tok.value, str) else str(tok.value)
    	table.add_row(tok.type, value, str(tok.lineno))
    
    console = Console()
    console.print(table, justify= "center", style='white on black')


if __name__ == '__main__':
    import sys 

    if len(sys.argv) != 2:
        print('Usage: python mclex.py filename')
        exit(0)
    '''    
    lexer = Lexer()
    data = open(sys.argv[1]).read()
    for tok in lexer.tokenize(data):
        print(tok)
    '''    
    pprint(open(sys.argv[1], encoding='utf-8').read())
    
  
