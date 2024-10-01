import ply.lex as lex
import ply.yacc as yacc
from flask import Flask, render_template, request

# Palabras reservadas
reserved = {
    'for': 'PALABRA_RESERVADA',
    'int': 'TIPO_DATO',
}

# Lista de tokens que se reconocerán
tokens = [
    'IDENTIFICADOR',
    'PAREN_APERTURA',
    'PAREN_CIERRE',
    'LLAVE_APERTURA',
    'LLAVE_CIERRE',
    'PUNTO_COMA'
] + list(reserved.values())

# Reglas de los tokens
t_ignore = ' \t'

# Expresión regular para tipos de datos
def t_TIPO_DATO(t):
    r'\bint\b'
    return t

# Expresiones regulares para paréntesis y llaves
def t_PAREN_APERTURA(t):
    r'\('
    return t

def t_PAREN_CIERRE(t):
    r'\)'
    return t

def t_LLAVE_APERTURA(t):
    r'\{'
    return t

def t_LLAVE_CIERRE(t):
    r'\}'
    return t

def t_PUNTO_COMA(t):
    r';'
    return t

# Expresión regular para palabras reservadas
def t_PALABRA_RESERVADA(t):
    r'\bfor\b'
    return t

# Regla para identificar identificadores
def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

# Manejar saltos de línea y contar líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejar errores
def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# Función para realizar el análisis léxico
def lexer_analysis(text):
    lexer.input(text)
    lexer.lineno = 1  # Reiniciar el contador de líneas
    tokens = []
    for tok in lexer:
        # Unificar 'PALABRA_RESERVADA' y 'TIPO_DATO' como "palabra reservada"
        if tok.type in ['PALABRA_RESERVADA', 'TIPO_DATO']:
            token_type = "palabra reservada"
        else:
            token_type = tok.type.replace("_", " ").lower()
        
        tokens.append({
            'line': tok.lineno,
            'column': tok.lexpos,
            'value': tok.value,
            'type': token_type
        })
    return tokens

# Análisis sintáctico
syntax_errors = []

def p_expression_main(p):
    'expression : TIPO_DATO IDENTIFICADOR PAREN_APERTURA PAREN_CIERRE LLAVE_APERTURA instrucciones LLAVE_CIERRE'
    p[0] = "estructura correcta"

def p_instrucciones(p):
    '''instrucciones : instruccion instrucciones
                     | instruccion
                     | empty'''
    pass

def p_instruccion(p):
    'instruccion : TIPO_DATO IDENTIFICADOR PUNTO_COMA'
    pass

def p_expression_incomplete(p):
    'expression : TIPO_DATO IDENTIFICADOR PAREN_APERTURA PAREN_CIERRE LLAVE_APERTURA'
    syntax_errors.append("Error de sintaxis: Falta llave de cierre '}' en la línea {}".format(p.lineno))

def p_expression_missing_semicolon(p):
    'instruccion : TIPO_DATO IDENTIFICADOR'
    syntax_errors.append(f"Error de sintaxis: Falta punto y coma ';' al final de la línea {p.lineno}")

def p_error(p):
    if p is None:
        syntax_errors.append("Error de sintaxis: Fin de archivo inesperado")
    else:
        syntax_errors.append(f"Error de sintaxis: Token inesperado '{p.value}' en la línea {p.lineno}")

# Definir una regla para "empty"
def p_empty(p):
    'empty :'
    pass

# Función para realizar el análisis sintáctico
def parser_analysis(text):
    global syntax_errors
    syntax_errors = []  # Resetear errores
    result = parser.parse(text)
    if not syntax_errors:  # Verificar si no hay errores
        return [{
            'line': 1,
            'structure': 'for',
            'correct': 'x',
            'incorrect': ''
        }]
    else:
        return []  # No se generan resultados válidos si hay errores

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Definir una ruta para la página principal
@app.route('/', methods=['GET', 'POST'])
def index():
    lex_tokens = []
    parse_results = []
    text = ""

    if request.method == 'POST':
        text = request.form['text']  # Texto ingresado en el formulario
        lex_tokens = lexer_analysis(text)  # Ejecutar el análisis léxico
        parse_results = parser_analysis(text)  # Ejecutar el análisis sintáctico

    return render_template('index3_1.html', text=text, lex_tokens=lex_tokens, parse_results=parse_results, syntax_errors=syntax_errors)

# Inicializar el lexer y el parser
lexer = lex.lex()
parser = yacc.yacc()

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)