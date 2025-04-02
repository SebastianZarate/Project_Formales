import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import random
import os
from PIL import Image, ImageTk

class GrammarProcessor:
    def __init__(self):
        self.grammar = {'type': None, 'start': None, 'productions': {}}

    def load_grammar(self, filepath):
        """
        Lee un archivo de gramática con el siguiente formato:
          type: <número>            (Ej. type: 3 o type: 2)
          start: <símbolo inicial>   (Ej. start: q0 o start: S)
          <no_terminal> -> <producción1> | <producción2> | ...
        En cada producción, los símbolos se separan por espacios.
        Se interpreta una producción vacía como la cadena ε.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            self.grammar['type'] = int(lines[0].split(':')[1].strip())
            self.grammar['start'] = lines[1].split(':')[1].strip()

            productions = {}
            for line in lines[2:]:
                if '->' not in line:
                    continue
                left, rights = line.split('->')
                left = left.strip()
                # Cada lado derecho puede tener varias alternativas separadas por |
                prods = []
                for prod in rights.split('|'):
                    prod = prod.strip()
                    # Si la cadena está vacía se interpreta como ε (cadena vacía)
                    if prod == "" or prod.lower() == "ε":
                        prods.append([])  # producción que representa epsilon
                    else:
                        prods.append(prod.split())
                productions[left] = prods
            self.grammar['productions'] = productions
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Formato de gramática inválido: {str(e)}")
            return False

    # ---------------------------
    # VALIDACIÓN DE CADENAS
    # ---------------------------
    def validate_string(self, string):
        """
        Valida la cadena según el tipo de gramática:
         - Tipo 3: se asume gramática regular y se simula un autómata.
         - Tipo 2: se realiza un análisis recursivo (backtracking) para gramáticas CFG.
        Retorna (True, derivation) si es válida o (False, derivation) en caso contrario.
        """
        if self.grammar['type'] == 3:
            return self._validate_regular(string)
        elif self.grammar['type'] == 2:
            derivation = []
            result = self._parse_cfg(self.grammar['start'], string, derivation)
            # La cadena es válida si se consume totalmente y no quedan caracteres.
            if result is not None and result == "":
                return True, derivation
            else:
                return False, derivation
        else:
            messagebox.showerror("Error", "Tipo de gramática no soportado para validación.")
            return False, []

    # Para gramáticas regulares (tipo 3)
    def _validate_regular(self, string):
        """
        Se simula un autómata finito derivado de la gramática regular.
        Se asume que la gramática es derecha-lineal.
        Cada producción es de la forma: estado -> terminal [siguiente_estado]
        Una producción que no indique siguiente estado se toma como final.
        """
        current = self.grammar['start']
        path = [current]
        remaining = string

        while remaining:
            char = remaining[0]
            found = False
            # Revisar todas las producciones para el estado actual
            for production in self.grammar['productions'].get(current, []):
                # La producción debe comenzar con el símbolo terminal
                if len(production) >= 1 and production[0] == char:
                    # Si hay un segundo símbolo, éste es el siguiente estado; de lo contrario,
                    # se asume que se llega a un estado final solo si ya se consumió la cadena.
                    next_state = production[1] if len(production) > 1 else None
                    found = True
                    path.append(f"{char} -> {next_state if next_state else 'FINAL'}")
                    current = next_state
                    remaining = remaining[1:]
                    break
            if not found:
                return False, path
        # La cadena es válida si se terminó en un transición que no esperaba más (es final)
        if current is None:
            return True, path
        else:
            # También se permite si existe una producción epsilon en el estado final
            for prod in self.grammar['productions'].get(current, []):
                if prod == []:
                    path.append("ε")
                    return True, path
            return False, path

    # Para gramáticas libres de contexto (tipo 2)
    def _parse_cfg(self, symbol, s, derivation):
        """
        Función recursiva que intenta derivar la cadena s a partir del símbolo dado.
        Retorna la porción de cadena no consumida si tiene éxito o None si falla.
        Acumula los pasos de derivación en la lista derivation.
        """
        # Si el símbolo es un no terminal (existe en las producciones)
        if symbol in self.grammar['productions']:
            # Probar cada producción
            for production in self.grammar['productions'][symbol]:
                # Guardar el paso actual de derivación
                step = f"{symbol} -> {' '.join(production) if production else 'ε'}"
                # Crear una copia de la derivación para este camino
                derivation_copy = derivation.copy()
                derivation_copy.append(step)
                # Intentar derivar la cadena a partir de esta producción
                remainder = s
                success = True
                # Para cada símbolo de la producción, derivar secuencialmente
                for prod_sym in production:
                    result = self._parse_cfg(prod_sym, remainder, derivation_copy)
                    if result is None:
                        success = False
                        break
                    else:
                        remainder = result
                if success:
                    # Se permite que la producción sea ε (lista vacía) y no consuma nada
                    derivation.clear()
                    derivation.extend(derivation_copy)
                    return remainder
            return None
        else:
            # El símbolo es terminal; se comprueba si s inicia con el símbolo
            if s.startswith(symbol):
                return s[len(symbol):]
            else:
                return None

    # ---------------------------
    # GENERACIÓN DE CADENAS
    # ---------------------------
    def generate_string(self, length):
        """
        Genera una cadena de longitud exacta que pertenezca al lenguaje.
        Se intenta por un número máximo de iteraciones.
        """
        if self.grammar['type'] == 3:
            return self._generate_regular(length)
        elif self.grammar['type'] == 2:
            return self._generate_cfg(length)
        else:
            messagebox.showerror("Error", "Tipo de gramática no soportado para generación.")
            return None

    def _generate_regular(self, length):
        """
        Genera una cadena para gramática regular simulando el autómata.
        Se realizan varios intentos hasta conseguir una cadena de longitud 'length'.
        """
        max_attempts = 1000
        for _ in range(max_attempts):
            current = self.grammar['start']
            generated = ""
            while True:
                # Si no hay producciones, detener la generación
                productions = self.grammar['productions'].get(current, [])
                if not productions:
                    break
                production = random.choice(productions)
                # Si la producción es epsilon, se detiene la expansión
                if production == []:
                    break
                # La producción debe tener al menos un terminal
                generated += production[0]
                # Actualizar estado: si existe siguiente estado, se continúa; de lo contrario se termina.
                if len(production) > 1:
                    current = production[1]
                else:
                    current = None
                    break
            if len(generated) == length:
                return generated
        return None

    def _generate_cfg(self, length):
        """
        Genera una cadena para gramática libre de contexto (tipo 2) mediante expansión aleatoria.
        Se intenta varias veces hasta obtener una cadena de longitud exacta.
        """
        max_attempts = 1000
        for _ in range(max_attempts):
            candidate = self._random_expand(self.grammar['start'])
            if candidate is not None and len(candidate) == length:
                return candidate
        return None

    def _random_expand(self, symbol):
        """
        Expande el símbolo de forma recursiva eligiendo aleatoriamente entre las producciones.
        Si el símbolo no es no terminal se retorna el propio símbolo.
        """
        if symbol in self.grammar['productions']:
            productions = self.grammar['productions'][symbol]
            production = random.choice(productions)
            result = ""
            for sym in production:
                result += self._random_expand(sym)
            return result
        else:
            return symbol

class ModernGrammarGUI:
    def __init__(self, master):
        self.master = master
        self.processor = GrammarProcessor()
        master.title("Procesador de Gramáticas")
        master.geometry("700x600")
        master.minsize(700, 600)
        self.configure_styles()
        self.create_widgets()
        self.load_default_logo()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        primary_color = "#4a6ea9"
        secondary_color = "#e6eef8" 
        accent_color = "#f0a500"

        style.configure('Primary.TButton', background=primary_color, foreground='white',
                        padding=8, font=('Arial', 10, 'bold'))
        style.map('Primary.TButton', background=[('active', accent_color), ('pressed', '#3d5d8f')])
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground=primary_color)
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'), foreground=primary_color)
        style.configure('Status.TLabel', font=('Arial', 10), padding=5)
        style.configure('Result.TLabel', font=('Arial', 12, 'bold'), padding=5)
        style.configure('Main.TFrame', background='white')
        style.configure('TNotebook', background='white')
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 10))
        style.map('TNotebook.Tab', background=[('selected', primary_color), ('active', secondary_color)],
                  foreground=[('selected', 'white'), ('active', 'black')])
        style.configure('TEntry', padding=8, font=('Arial', 10))

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=10)

        # Logo
        self.logo_frame = ttk.Frame(top_frame, width=100, height=100)
        self.logo_frame.pack(side=tk.LEFT, padx=10)
        self.lbl_logo = ttk.Label(self.logo_frame)
        self.lbl_logo.pack(pady=5)

        title_frame = ttk.Frame(top_frame)
        title_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Label(title_frame, text="Procesador de Gramáticas", style='Title.TLabel').pack(anchor=tk.W)
        ttk.Label(title_frame, text="Valida y genera cadenas basadas en gramáticas formales",
                  style='Status.TLabel').pack(anchor=tk.W, pady=5)

        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)
        self.btn_load = ttk.Button(file_frame, text="Cargar Gramática", style='Primary.TButton',
                                    command=self.load_grammar)
        self.btn_load.pack(side=tk.LEFT, padx=5)
        self.lbl_status = ttk.Label(file_frame, text="No se ha cargado ninguna gramática", style='Status.TLabel')
        self.lbl_status.pack(side=tk.LEFT, padx=10)

        self.notebook = ttk.Notebook(main_frame)
        validate_tab = ttk.Frame(self.notebook)
        self.create_validate_tab(validate_tab)
        generate_tab = ttk.Frame(self.notebook)
        self.create_generate_tab(generate_tab)
        self.notebook.add(validate_tab, text="Validar Cadena")
        self.notebook.add(generate_tab, text="Generar Cadena")
        self.notebook.pack(expand=True, fill=tk.BOTH, pady=10)

        status_bar = ttk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Label(status_bar, text="Procesador de Gramáticas v1.0", style='Status.TLabel').pack(side=tk.LEFT)

    def create_validate_tab(self, parent):
        padding_frame = ttk.Frame(parent, padding=20)
        padding_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(padding_frame, text="Validación de Cadenas", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(0, 10))
        ttk.Label(padding_frame, text="Ingrese la cadena a validar:").pack(anchor=tk.W, pady=(10, 5))
        self.txt_validate = ttk.Entry(padding_frame, width=40)
        self.txt_validate.pack(fill=tk.X, pady=(0, 10))
        self.btn_validate = ttk.Button(padding_frame, text="Validar Cadena", style='Primary.TButton',
                                       command=self.validate_string)
        self.btn_validate.pack(pady=10)
        result_frame = ttk.Frame(padding_frame)
        result_frame.pack(fill=tk.X, pady=10)
        ttk.Label(result_frame, text="Resultado:").pack(anchor=tk.W)
        self.lbl_result = ttk.Label(result_frame, text="", style='Result.TLabel')
        self.lbl_result.pack(anchor=tk.W)
        ttk.Label(padding_frame, text="Derivación:").pack(anchor=tk.W, pady=(10, 5))
        text_frame = ttk.Frame(padding_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_derivation = tk.Text(text_frame, height=8, width=50, state=tk.DISABLED,
                                      font=('Consolas', 10), yscrollcommand=scrollbar.set)
        self.txt_derivation.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.txt_derivation.yview)

    def create_generate_tab(self, parent):
        padding_frame = ttk.Frame(parent, padding=20)
        padding_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(padding_frame, text="Generación de Cadenas", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(0, 10))
        input_frame = ttk.Frame(padding_frame)
        input_frame.pack(fill=tk.X, pady=10)
        ttk.Label(input_frame, text="Longitud de la cadena:").pack(side=tk.LEFT, padx=(0, 10))
        self.spn_length = ttk.Spinbox(input_frame, from_=1, to=100, width=5, font=('Arial', 10))
        self.spn_length.set(5)
        self.spn_length.pack(side=tk.LEFT)
        self.btn_generate = ttk.Button(padding_frame, text="Generar Cadena", style='Primary.TButton',
                                       command=self.generate_string)
        self.btn_generate.pack(pady=10)
        result_frame = ttk.Frame(padding_frame)
        result_frame.pack(fill=tk.X, pady=10)
        ttk.Label(result_frame, text="Cadena generada:").pack(anchor=tk.W)
        self.lbl_generated = ttk.Label(result_frame, text="", style='Result.TLabel')
        self.lbl_generated.pack(anchor=tk.W, pady=5)
        ttk.Label(padding_frame, text="Historial de cadenas generadas:").pack(anchor=tk.W, pady=(10, 5))
        list_frame = ttk.Frame(padding_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        scrollbar2 = ttk.Scrollbar(list_frame)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        self.lst_history = tk.Listbox(list_frame, height=6, font=('Consolas', 10), yscrollcommand=scrollbar2.set)
        self.lst_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.config(command=self.lst_history.yview)

    def load_default_logo(self):
        # Se asume que "logo.png" se encuentra en el directorio actual
        logo_path = os.path.join(os.getcwd(), "logo.png")
        try:
            original_image = Image.open(logo_path)
            max_size = 80
            width, height = original_image.size
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(resized_image)
            self.lbl_logo.config(image=self.logo_image)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el logo: {str(e)}")

    def load_grammar(self):
        filepath = filedialog.askopenfilename(filetypes=[("Archivos de gramática", "*.grm")])
        if filepath:
            if self.processor.load_grammar(filepath):
                grammar_type = self.processor.grammar['type']
                grammar_name = os.path.basename(filepath)
                self.lbl_status.config(text=f"Gramática cargada: {grammar_name} (Tipo {grammar_type})")
                if grammar_type == 3:
                    grammar_desc = "Regular"
                elif grammar_type == 2:
                    grammar_desc = "Libre de Contexto"
                else:
                    grammar_desc = "No soportado"
                self.notebook.tab(0, text=f"Validar ({grammar_desc})")
                self.notebook.tab(1, text=f"Generar ({grammar_desc})")

    def validate_string(self):
        if not self.processor.grammar['productions']:
            messagebox.showwarning("Advertencia", "Primero cargue una gramática")
            return
        input_str = self.txt_validate.get().strip()
        if not input_str:
            messagebox.showwarning("Advertencia", "Ingrese una cadena para validar")
            return
        valid, derivation = self.processor.validate_string(input_str)
        self.txt_derivation.config(state=tk.NORMAL)
        self.txt_derivation.delete(1.0, tk.END)
        if valid:
            self.lbl_result.config(text="Cadena VÁLIDA ✓", foreground="green")
            self.txt_derivation.insert(tk.END, "\n".join(derivation))
        else:
            self.lbl_result.config(text="Cadena INVÁLIDA ✗", foreground="red")
            self.txt_derivation.insert(tk.END, "\n".join(derivation))
        self.txt_derivation.config(state=tk.DISABLED)

    def generate_string(self):
        if not self.processor.grammar['productions']:
            messagebox.showwarning("Advertencia", "Primero cargue una gramática")
            return
        try:
            length = int(self.spn_length.get())
            if length <= 0:
                messagebox.showwarning("Advertencia", "La longitud debe ser un número positivo")
                return
            generated = self.processor.generate_string(length)
            if generated:
                self.lbl_generated.config(text=generated)
                self.lst_history.insert(0, generated)
                if self.lst_history.size() > 100:
                    self.lst_history.delete(100)
            else:
                self.lbl_generated.config(text="No se pudo generar una cadena válida")
        except ValueError:
            messagebox.showerror("Error", "Longitud inválida")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernGrammarGUI(root)
    root.mainloop()