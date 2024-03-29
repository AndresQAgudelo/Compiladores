import argparse
import sly


from mclex import Lexer
from mcast import (TranslationUnit,
    FuncDefinition,
    WhileLoop,
    ForLoop,
    Continue,
    Binary,
    Unary,
    Variable,
    Literal,
    ExprStmt,
    Return,
    IfStmt,
    Break,
    VarDefinition
    ) 

class Parser(sly.Parser):
    debugfile = "minic.txt"

    tokens = Lexer.tokens
    
    @_("translation_unit")
    def program(self, p):
        return TranslationUnit( p.translation_unit )

    @_("external_declaration")
    def translation_unit(self, p):
        return [ p.external_declaration ]

    @_("translation_unit external_declaration")
    def translation_unit(self, p):
        return p.translation_unit + [ p.external_declaration ]

    @_("function_definition", 
       "declaration")
    def external_declaration(self, p):
        return p[0]

    @_("type_specifier declarator compound_statement")
    def function_definition(self, p):
        return FuncDefinition( p.type_specifier, p.declarator[0], p.declarator[1], p.compound_statement )

    @_("STATIC type_specifier declarator compound_statement")
    def function_definition(self, p):
        return FuncDefinition(p.type_specifier, p.declarator[0], p.declarator[1], p.compound_statement, True)

    @_("type_specifier declarator ';'")
    def declaration(self, p):
        return VarDefinition(p.type_specifier,  p.declarator)

    @_("EXTERN type_specifier declarator ';'")
    def declaration(self, p):
        return VarDefinition(p.type_specifier,  p.declarator, None)

    @_("empty")
    def declaration_list_opt(self, p):
        pass

    @_("declaration_list")
    def declaration_list_opt(self, p):
        return p.declaration_list

    @_("declaration")
    def declaration_list(self, p):
        return [ p.declaration ]

    @_("declaration_list declaration")
    def declaration_list(self, p):
        return p.declaration_list + [ p.declaration ]

    @_("INT", "FLOAT", "CHAR", "VOID")
    def type_specifier(self, p):
        return p[0]

    @_("direct_declarator")
    def declarator(self, p):
        return p.direct_declarator

    @_("'*' declarator")
    def declarator(self, p):
        return (p[0], p.declarator)

    @_("ID")
    def direct_declarator(self, p):
        return Variable(p.ID)

    @_("direct_declarator '(' parameter_type_list ')'")
    def direct_declarator(self, p):
        return ( p.direct_declarator, p.parameter_type_list )

    @_("direct_declarator '(' ')'")
    def direct_declarator(self, p):
        return p.direct_declarator

    @_("parameter_list")
    def parameter_type_list(self, p):
        return p.parameter_list

    @_("parameter_list ',' ELLIPSIS")
    def parameter_type_list(self, p):
        return (p.parameter_list, p.ELLIPSIS)

    @_("parameter_declaration")
    def parameter_list(self, p):
        return [ p.parameter_declaration ]

    @_("parameter_list ',' parameter_declaration")
    def parameter_list(self, p):
        return p.parameter_list + [ p.parameter_declaration ]

    @_("type_specifier declarator")
    def parameter_declaration(self, p):
        return (p.type_specifier, p.declarator)

    @_("'{' declaration_list_opt statement_list '}'")
    def compound_statement(self, p):
        return (p.declaration_list_opt, p.statement_list)
    
    @_("'{' declaration_list_opt '}'")
    def compound_statement(self, p):
        return p.declaration_list_opt

    @_("expression ';'")
    def expression_statement(self, p):
        return ExprStmt(p.expression)

    @_("equality_expression")
    def expression(self, p):
        return p.equality_expression

    @_("equality_expression '='   expression",
       "equality_expression ADDEQ expression",
       "equality_expression SUBEQ expression")
    def expression(self, p):
        return Binary(p[1], p.equality_expression, p.expression)
        
    @_("relational_expression")
    def equality_expression(self, p):
        return p.relational_expression

    @_("equality_expression EQ relational_expression",
       "equality_expression NE relational_expression")
    def equality_expression(self, p):
        return Binary(p[1], p.equality_expression, p.relational_expression)

    @_("additive_expression")
    def relational_expression(self, p):
        return p.additive_expression

    @_("relational_expression '<' additive_expression",
       "relational_expression LE  additive_expression",
       "relational_expression '>' additive_expression",
       "relational_expression GE  additive_expression")
    def relational_expression(self, p):
        return Binary(p[1], p.relational_expression, p.additive_expression)

    @_("primary_expression")
    def postfix_expression(self, p):
        return p.primary_expression

    @_("postfix_expression '(' argument_expression_list ')'")
    def postfix_expression(self, p):
        return (p.postfix_expression, p.argument_expression_list)

    @_("postfix_expression '(' ')'")
    def postfix_expression(self, p):
        return p.postfix_expression

    @_("postfix_expression '[' expression ']'")
    def postfix_expression(self, p):
        return (p.postfix_expression, p.expression)

    @_("expression")
    def argument_expression_list(self, p):
        return p.expression

    @_("argument_expression_list ',' expression")
    def argument_expression_list(self, p):
        return (p.argument_expression_list, p.expression)

    @_("postfix_expression")
    def unary_expression(self, p):
        return p.postfix_expression

    @_("'-' unary_expression")
    def unary_expression(self, p):
        return Unary(p[0], p.unary_expression)

    @_("'+' unary_expression")
    def unary_expression(self, p):
        return Unary(p[0], p.unary_expression )

    @_("'!' unary_expression")
    def unary_expression(self, p):
        return Unary(p[0], p.unary_expression)

    @_("'*' unary_expression")
    def unary_expression(self, p):
        return Unary(p[0], p.unary_expression)

    @_("'&' unary_expression")
    def unary_expression(self, p):
        return Unary(p[0], p.unary_expression)

    @_("unary_expression")
    def mult_expression(self, p):
        return p.unary_expression

    @_("mult_expression '*' unary_expression",
       "mult_expression '/' unary_expression",
       "mult_expression '%' unary_expression")
    def mult_expression(self, p):
        return Binary(p[1], p.mult_expression, p.unary_expression )

    @_("mult_expression")
    def additive_expression(self, p):
        return p.mult_expression

    @_("additive_expression '+' mult_expression",
       "additive_expression '-' mult_expression")
    def additive_expression(self, p):
        return (p[1], p.additive_expression, p.mult_expression )

    @_("ID")
    def primary_expression(self, p):
        return Literal(p.ID)

    @_("INUMBER")
    def primary_expression(self, p):
        return Literal(p.INUMBER)

    @_("FNUMBER")
    def primary_expression(self, p):
        return Literal(p.FNUMBER)

    @_("CHARACTER")
    def primary_expression(self, p):
        return Literal(p.CHARACTER)

    @_("string_literal")
    def primary_expression(self, p):
        return p.string_literal

    @_("'(' expression ')'")
    def primary_expression(self, p):
        return p.expression

    @_("STRING")
    def string_literal(self, p):
        return Literal(p.STRING)

    @_("string_literal STRING")
    def string_literal(self, p):
        return (p.string_literal + p.STRING)

    @_("compound_statement",
       "expression_statement",
       "selection_statement",
       "iteration_statement",
       "jumstatement")
    def statement(self, p):
        return p[0]

    @_("RETURN ';'")
    def jumstatement(self, p):
        return p.RETURN

    @_("RETURN expression ';'")
    def jumstatement(self, p):
        return Return(p.expression)

    @_("BREAK ';'")
    def jumstatement(self, p):
        return Break()

    @_("CONTINUE ';'")
    def jumstatement(self, p):
        return Continue()

    @_("WHILE '(' expression ')' statement")
    def iteration_statement(self, p):
        return WhileLoop( p.expression, p.statement )

    @_("FOR '(' expression_statement expression_statement expression ')' statement")
    def iteration_statement(self, p):
        return ForLoop( p.expression_statement0, p.expression_statement1, p.expression, p.statement )

    @_("IF '(' expression ')' '{' statement '}'")
    def selection_statement(self, p):
       return IfStmt(p.expression, p.statement, None)
    
    @_("IF '(' expression ')' '{' statement '}' ELSE '{' statement '}'")
    def selection_statement(self, p):
        return IfStmt(p.expression, p.statement0, p.statement1)


    @_("statement")
    def statement_list(self, p):
        return [ p.statement ]

    @_("statement_list statement")
    def statement_list(self, p):
        return p.statement_list + [ p.statement ]

    @_("")
    def empty(self, p):
        pass

    def error(self, p):
        lineno = p.lineno if p else 'EOF'
        value  = p.value  if p else 'EOF'
        print(f"{lineno}: Error de Sintaxis en {value}")

        raise SyntaxError()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 2:
        print(f"usage: python {sys.argv[0]} [ fname1 [ fname2 ... ] ]   --ast")
        exit(1)
    
    l = Lexer()
    p = Parser()
    txt = open(sys.argv[1], encoding='utf-8').read()

    ast = p.parse(l.tokenize(txt))
    
    print(ast)