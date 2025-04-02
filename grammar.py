from tkinter import messagebox

class Grammar:
    def __init__(self):
        self.type = None
        self.start = None
        self.productions = {}

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

            self.type = int(lines[0].split(':')[1].strip())
            self.start = lines[1].split(':')[1].strip()

            productions = {}
            for line in lines[2:]:
                if '->' not in line:
                    continue
                left, rights = line.split('->')
                left = left.strip()
                prods = []
                for prod in rights.split('|'):
                    prod = prod.strip()
                    if prod == "" or prod.lower() == "ε":
                        prods.append([])  # producción que representa ε
                    else:
                        prods.append(prod.split())
                productions[left] = prods
            self.productions = productions
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Formato de gramática inválido: {str(e)}")
            return False