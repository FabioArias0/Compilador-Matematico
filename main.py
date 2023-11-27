import tkinter as tk
from tkinter import scrolledtext
from ply import lex, yacc

# Definición de tokens
tokens = (
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
)

# Reglas de expresiones regulares para tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'

# Regla de token para números
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Manejo de errores de caracteres no reconocidos
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Analizador léxico
lexer = lex.lex()

# Definición de la gramática
def p_expression(p):
    '''
    expression : expression PLUS term
               | expression MINUS term
               | term
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[2] == '+':
            p[0] = (p[1], p[3], '+')
        elif p[2] == '-':
            p[0] = (p[1], p[3], '-')

def p_term(p):
    '''
    term : term TIMES factor
         | term DIVIDE factor
         | factor
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[2] == '*':
            p[0] = (p[1], p[3], '*')
        elif p[2] == '/':
            p[0] = (p[1], p[3], '/')

def p_factor(p):
    '''
    factor : NUMBER
           | LPAREN expression RPAREN
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

# Manejo de errores de sintaxis
def p_error(p):
    print(f"Syntax error at '{p.value}'")

# Analizador sintáctico
parser = yacc.yacc()

class SimpleIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Compilador Matemático")

        # Cuadro de texto para escribir código
        self.code_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=10)
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Cuadro para mostrar el resultado, los tokens, el código intermedio y la tabla de símbolos
        self.result_frame = tk.Frame(root, width=40, height=10, bg="lightgray")
        self.result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Etiqueta en la parte superior del cuadro de resultado
        self.result_label = tk.Label(self.result_frame, text="Resultado compilado:", bg="lightgray")
        self.result_label.pack(side=tk.TOP)

        # Cuadro de texto para mostrar el resultado
        self.result_text = tk.Text(self.result_frame, wrap=tk.WORD, width=40, height=1)
        self.result_text.pack(side=tk.TOP)

        # Cuadro de texto para mostrar los tokens en la parte superior del cuadro de resultado
        self.tokens_text = scrolledtext.ScrolledText(self.result_frame, wrap=tk.WORD, width=40, height=10)
        self.tokens_text.pack(side=tk.BOTTOM)

        # Cuadro de texto para mostrar el código intermedio en la parte media del cuadro de resultado
        self.intermediate_code_text = scrolledtext.ScrolledText(self.result_frame, wrap=tk.WORD, width=40, height=10)
        self.intermediate_code_text.pack(side=tk.BOTTOM)

        # Cuadro de texto para mostrar la tabla de símbolos en la parte inferior del cuadro de resultado
        self.symbols_text = scrolledtext.ScrolledText(self.result_frame, wrap=tk.WORD, width=40, height=10)
        self.symbols_text.pack(side=tk.BOTTOM)

        # Cuadro de texto para mostrar el código traducido a C++ en la parte inferior del cuadro de resultado
        self.cpp_code_text = scrolledtext.ScrolledText(self.result_frame, wrap=tk.WORD, width=40, height=10)
        self.cpp_code_text.pack(side=tk.BOTTOM)

        # Botón para compilar el código
        self.compile_button = tk.Button(root, text="Compilar", command=self.compile_code)
        self.compile_button.pack(side=tk.BOTTOM)

    def compile_code(self):
        # Obtener el código del cuadro de texto
        code = self.code_text.get("1.0", tk.END).strip()

        # Verificar si el código está vacío
        if not code:
            self.result_label.config(text="Resultado compilado: No input provided")
            return

        # Analizar léxicamente e imprimir los tokens en la consola
        lexer.input(code)
        tokens_output = "Tokens: \n"
        symbols_output = "Tabla de Símbolos:\nTipo\tToken\n"
        for tok in lexer:
            tokens_output += f"{tok.type}: {tok.value}\n"
            symbols_output += f"{get_token_type(tok.type)}\t{tok.value}\n"

        # Analizar sintácticamente e imprimir el resultado, los tokens y el código intermedio en el cuadro de resultado
        try:
            result = parser.parse(code)
            result_value = evaluate_expression(result)
            result_text = f"Resultado compilado: {result_value}"
            self.result_label.config(text=result_text)
            self.result_text.delete("1.0", tk.END)  # Limpiar el cuadro de resultado
            self.result_text.insert(tk.END, str(result_value))
            self.tokens_text.delete("1.0", tk.END)  # Limpiar el cuadro de tokens
            self.tokens_text.insert(tk.END, tokens_output)

            # Generar el código de tres direcciones
            intermediate_code = generate_intermediate_code(result)
            intermediate_code_text = "Código Intermedio:\n" + "\n".join(intermediate_code)
            self.intermediate_code_text.delete("1.0", tk.END)  # Limpiar el cuadro de código intermedio
            self.intermediate_code_text.insert(tk.END, intermediate_code_text)

            # Mostrar la tabla de símbolos en el cuadro de símbolos
            self.symbols_text.delete("1.0", tk.END)  # Limpiar el cuadro de símbolos
            self.symbols_text.insert(tk.END, symbols_output)

            # Generar el código traducido a C++
            cpp_code = generate_cpp_code(result)
            cpp_code_text = "C++ Code:\n" + cpp_code
            self.cpp_code_text.delete("1.0", tk.END)  # Limpiar el cuadro de código C++
            self.cpp_code_text.insert(tk.END, cpp_code_text)
        except Exception as e:
            result_text = f"Error: {str(e)}"
            self.result_label.config(text=result_text)
            self.result_text.delete("1.0", tk.END)  # Limpiar el cuadro de resultado
            self.tokens_text.delete("1.0", tk.END)  # Limpiar el cuadro de tokens
            self.intermediate_code_text.delete("1.0", tk.END)  # Limpiar el cuadro de código intermedio
            self.symbols_text.delete("1.0", tk.END)  # Limpiar el cuadro de símbolos
            self.cpp_code_text.delete("1.0", tk.END)  # Limpiar el cuadro de código C++

def evaluate_expression(node):
    # Función para evaluar la expresión matemática
    if isinstance(node, tuple):
        left, right, operator = node
        left_val = evaluate_expression(left)
        right_val = evaluate_expression(right)

        if operator == '+':
            return left_val + right_val
        elif operator == '-':
            return left_val - right_val
        elif operator == '*':
            return left_val * right_val
        elif operator == '/':
            if right_val != 0:
                return left_val / right_val
            else:
                raise ValueError("Division by zero")
    else:
        return node

def generate_intermediate_code(expression):
    # Función para generar el código de tres direcciones
    code = []

    def generate_code_helper(node):
        nonlocal code

        if isinstance(node, tuple):
            left, right, operator = node
            temp_var = f"t{len(code) + 1}"

            generate_code_helper(left)
            generate_code_helper(right)

            code.append(f"{temp_var} = {left} {operator} {right}")
            return temp_var
        else:
            return node

    generate_code_helper(expression)
    return code

def generate_cpp_code(expression):
    # Función para generar el código traducido a C++
    def generate_cpp_code_helper(node):
        if isinstance(node, tuple):
            left, right, operator = node

            left_cpp = generate_cpp_code_helper(left)
            right_cpp = generate_cpp_code_helper(right)

            return f"({left_cpp} {operator} {right_cpp})"
        else:
            return str(node)

    return generate_cpp_code_helper(expression)

def get_token_type(token):
    # Función para determinar el tipo de token
    if token in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE']:
        return "Operador"
    elif token == 'NUMBER':
        return "Digito"
    elif token in ['LPAREN', 'RPAREN']:
        return "Simbolo Especial"
    else:
        return "Identificador"  # Se asume que cualquier otro token es un identificador

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleIDE(root)
    root.mainloop()
