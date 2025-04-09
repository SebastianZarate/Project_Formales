from tkinter import messagebox
from typing import List, Dict, Set, Tuple

class Grammar:
    """
    Representa una gramática libre de contexto (Tipo 2)
    o una gramática regular (Tipo 3).
    """
    def __init__(self, nonterminals=None, terminals=None, start="", productions=None):
        """
        :param nonterminals: Conjunto de símbolos no terminales (N).
        :param terminals: Conjunto de símbolos terminales (T).
        :param start: Símbolo inicial (S).
        :param productions: Diccionario con clave = no terminal, 
                            valor = lista de posibles producciones.
                            Ej: { "S": [["a","S","b"], ["ε"]] }
        """
        self.nonterminals = nonterminals if nonterminals is not None else []
        self.terminals = terminals if terminals is not None else []
        self.start = start
        self.productions = productions if productions is not None else {}

    @staticmethod
    def from_text(text: str):
        """
        Crea una Gramática a partir de un texto con un formato sencillo.
        Ejemplo de formato:
        
            type: 2
            NonTerminals: S
            Terminals: a, b
            StartSymbol: S
            Productions:
            S -> a S b | ε

        Retorna un objeto Grammar.
        """
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        grammar_type = None
        nonterminals = set()
        terminals = set()
        start = None
        productions = {}
        
        section = None
        for line in lines:
            if line.lower().startswith("type:"):
                # Extraer el tipo de gramática
                try:
                    grammar_type = int(line.split(":", 1)[1].strip())
                except ValueError:
                    raise ValueError("El valor de 'type' debe ser un número (2 o 3).")
            elif line.startswith("NonTerminals:"):
                section = "N"
                parts = line.split(":", 1)[1].strip()
                nonterminals = set(p.strip() for p in parts.split(",") if p.strip())
            elif line.startswith("Terminals:"):
                section = "T"
                parts = line.split(":", 1)[1].strip()
                terminals = set(p.strip() for p in parts.split(",") if p.strip())
            elif line.startswith("start:"):
                section = "S"
                start = line.split(":", 1)[1].strip()
            elif line.startswith("Productions:"):
                section = "P"
            else:
                # Si no se ha especificado sección y la línea contiene "->", asumir producción
                if "->" in line:
                    section = "P"
                if section == "P":
                    left_right = line.split("->")
                    if len(left_right) != 2:
                        continue  # Ignorar líneas mal formadas
                    left = left_right[0].strip()
                    right = left_right[1].strip()
                    options = [opt.strip() for opt in right.split("|") if opt.strip()]
                    if left not in productions:
                        productions[left] = []
                    for opt in options:
                        symbols = opt.split()
                        productions[left].append(symbols)
        
        grammar = Grammar(nonterminals, terminals, start, productions)
        if grammar_type is not None:
            grammar.type = grammar_type
        else:
            grammar.type = "Desconocido"
        return grammar


    @staticmethod
    def from_file(filename: str):
        """
        Crea la Gramática leyendo desde un archivo con el mismo formato de from_text.
        """
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
        return Grammar.from_text(text)

    def __str__(self):
        result = []
        result.append("No Terminales: " + str(self.nonterminals))
        result.append("Terminales: " + str(self.terminals))
        result.append("Símbolo Inicial: " + str(self.start))
        result.append("Producciones:")
        for nt, prods in self.productions.items():
            prod_strs = []
            for p in prods:
                prod_strs.append(" ".join(p))
            result.append(f"  {nt} -> {' | '.join(prod_strs)}")
        return "\n".join(result)
