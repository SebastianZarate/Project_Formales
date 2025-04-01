import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import random

class GrammarProcessor:
    def __init__(self):
        self.grammar = {'type': None, 'productions': {}, 'start': None}
        
    def load_grammar(self, filepath):
        try:
            with open(filepath, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
                
            self.grammar['type'] = int(lines[0].split(':')[1])
            self.grammar['start'] = lines[1].split(':')[1].strip()
            
            for line in lines[2:]:
                left, right = line.split('->')
                left = left.strip()
                right = [prod.strip().split() for prod in right.split('|')]
                self.grammar['productions'][left] = right
                
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Formato de gramática inválido: {str(e)}")
            return False

    def validate_string(self, string):
        if self.grammar['type'] == 3:
            return self._validate_regular(string)
        else:
            return self._validate_context_free(string, self.grammar['start'], [])

    def _validate_regular(self, string):
        # Implementación de autómata finito
        current = self.grammar['start']
        path = [current]
        
        for char in string:
            found = False
            for production in self.grammar['productions'].get(current, []):
                if len(production) == 1 and production[0] == char:
                    current = production[0]
                    found = True
                    break
                elif len(production) == 2 and production[0] == char:
                    current = production[1]
                    found = True
                    break
            if not found:
                return False, []
            path.append(current)
            
        return current in self.grammar['productions'].get('FINAL', []), path

    def _validate_context_free(self, string, current_symbol, derivation):
        if not string and not current_symbol:
            return True, derivation
            
        if current_symbol in self.grammar['productions']:
            for production in self.grammar['productions'][current_symbol]:
                new_derivation = derivation + [f"{current_symbol} -> {' '.join(production)}"]
                result, path = self._validate_context_free(string, production, new_derivation)
                if result:
                    return True, path
            return False, []
        elif current_symbol == string[0:len(current_symbol)]:
            return self._validate_context_free(string[len(current_symbol):], '', derivation)
        else:
            return False, []

    def generate_string(self, length):
        if self.grammar['type'] == 3:
            return self._generate_regular(length)
        else:
            return self._generate_context_free(length, self.grammar['start'])

    def _generate_regular(self, length):
        current = self.grammar['start']
        generated = []
        
        while len(generated) < length:
            productions = self.grammar['productions'].get(current, [])
            if not productions:
                break
            production = random.choice(productions)
            generated.append(production[0])
            current = production[1] if len(production) > 1 else None
            
        return ''.join(generated) if len(generated) == length else None

    def _generate_context_free(self, length, symbol):
        if symbol in self.grammar['productions']:
            production = random.choice(self.grammar['productions'][symbol])
            return ''.join([self._generate_context_free(length, s) for s in production])
        else:
            return symbol if len(symbol) <= length else ''

class GrammarGUI:
    def __init__(self, master):
        self.master = master
        self.processor = GrammarProcessor()
        
        master.title("Procesador de Gramáticas")
        self.create_widgets()

    def create_widgets(self):
        # Frame superior para carga de archivo
        top_frame = ttk.Frame(self.master, padding="10")
        top_frame.pack(fill=tk.X)
        
        self.btn_load = ttk.Button(top_frame, text="Cargar Gramática", command=self.load_grammar)
        self.btn_load.pack(side=tk.LEFT)
        
        self.lbl_status = ttk.Label(top_frame, text="No se ha cargado ninguna gramática")
        self.lbl_status.pack(side=tk.LEFT, padx=10)
        
        # Panel de pestañas
        notebook = ttk.Notebook(self.master)
        
        # Pestaña de validación
        validate_tab = ttk.Frame(notebook)
        self.create_validate_tab(validate_tab)
        
        # Pestaña de generación
        generate_tab = ttk.Frame(notebook)
        self.create_generate_tab(generate_tab)
        
        notebook.add(validate_tab, text="Validar Cadena")
        notebook.add(generate_tab, text="Generar Cadena")
        notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def create_validate_tab(self, parent):
        ttk.Label(parent, text="Cadena a validar:").pack(anchor=tk.W)
        self.txt_validate = ttk.Entry(parent, width=40)
        self.txt_validate.pack(fill=tk.X)
        
        self.btn_validate = ttk.Button(parent, text="Validar", command=self.validate_string)
        self.btn_validate.pack(pady=5)
        
        self.lbl_result = ttk.Label(parent, text="")
        self.lbl_result.pack()
        
        self.txt_derivation = tk.Text(parent, height=8, width=50, state=tk.DISABLED)
        self.txt_derivation.pack(pady=10)

    def create_generate_tab(self, parent):
        ttk.Label(parent, text="Longitud de la cadena:").pack(anchor=tk.W)
        self.spn_length = ttk.Spinbox(parent, from_=1, to=100, width=5)
        self.spn_length.pack(anchor=tk.W)
        
        self.btn_generate = ttk.Button(parent, text="Generar", command=self.generate_string)
        self.btn_generate.pack(pady=5)
        
        self.lbl_generated = ttk.Label(parent, text="")
        self.lbl_generated.pack()

    def load_grammar(self):
        filepath = filedialog.askopenfilename(filetypes=[("Archivos de gramática", "*.grm")])
        if filepath:
            if self.processor.load_grammar(filepath):
                self.lbl_status.config(text=f"Gramática tipo {self.processor.grammar['type']} cargada")

    def validate_string(self):
        if not self.processor.grammar['productions']:
            messagebox.showwarning("Advertencia", "Primero cargue una gramática")
            return
            
        string = self.txt_validate.get()
        is_valid, path = self.processor.validate_string(string)
        
        self.txt_derivation.config(state=tk.NORMAL)
        self.txt_derivation.delete(1.0, tk.END)
        
        if is_valid:
            self.lbl_result.config(text="Cadena VÁLIDA", foreground="green")
            self.txt_derivation.insert(tk.END, "Derivación:\n" + "\n".join(path))
        else:
            self.lbl_result.config(text="Cadena INVÁLIDA", foreground="red")
            
        self.txt_derivation.config(state=tk.DISABLED)

    def generate_string(self):
        if not self.processor.grammar['productions']:
            messagebox.showwarning("Advertencia", "Primero cargue una gramática")
            return
            
        try:
            length = int(self.spn_length.get())
            generated = self.processor.generate_string(length)
            if generated:
                self.lbl_generated.config(text=f"Cadena generada: {generated}")
            else:
                self.lbl_generated.config(text="No se pudo generar una cadena válida")
        except ValueError:
            messagebox.showerror("Error", "Longitud inválida")

if __name__ == "__main__":
    root = tk.Tk()
    app = GrammarGUI(root)
    root.mainloop()