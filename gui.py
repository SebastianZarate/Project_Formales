import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from grammar import Grammar
from grammar_validator import GrammarValidator
from grammar_generator import GrammarGenerator

class ModernGrammarGUI:
    def __init__(self, master):
        self.master = master
        # Inicialmente, la gramática se crea sin contenido.
        self.grammar = Grammar()
        self.validator = None
        self.generator = None
        
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
            if self.grammar.load_grammar(filepath):
                # Crear instancias de validación y generación usando la gramática cargada
                self.validator = GrammarValidator(self.grammar)
                self.generator = GrammarGenerator(self.grammar)
                grammar_type = self.grammar.type
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
        if not self.grammar.productions or self.validator is None:
            messagebox.showwarning("Advertencia", "Primero cargue una gramática")
            return
        input_str = self.txt_validate.get().strip()
        if not input_str:
            messagebox.showwarning("Advertencia", "Ingrese una cadena para validar")
            return
        valid, derivation = self.validator.validate_string(input_str)
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
        if not self.grammar.productions or self.generator is None:
            messagebox.showwarning("Advertencia", "Primero cargue una gramática")
            return
        try:
            length = int(self.spn_length.get())
            if length <= 0:
                messagebox.showwarning("Advertencia", "La longitud debe ser un número positivo")
                return
            generated = self.generator.generate_string(length)
            if generated:
                self.lbl_generated.config(text=generated)
                self.lst_history.insert(0, generated)
                if self.lst_history.size() > 100:
                    self.lst_history.delete(100)
            else:
                self.lbl_generated.config(text="No se pudo generar una cadena válida")
        except ValueError:
            messagebox.showerror("Error", "Longitud inválida")