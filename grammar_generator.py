from tkinter import messagebox
import random

class GrammarGenerator:
    def __init__(self, grammar):
        """
        Recibe una instancia de Grammar.
        """
        self.grammar = grammar

    def generate_string(self, length):
        """
        Genera una cadena de longitud exacta que pertenezca al lenguaje.
        """
        if self.grammar.type == 3:
            return self._generate_regular(length)
        elif self.grammar.type == 2:
            return self._generate_cfg(length)
        else:
            messagebox.showerror("Error", "Tipo de gramática no soportado para generación.")
            return None

    def _generate_regular(self, length):
        max_attempts = 1000
        for _ in range(max_attempts):
            current = self.grammar.start
            generated = ""
            while True:
                productions = self.grammar.productions.get(current, [])
                if not productions:
                    break
                production = random.choice(productions)
                if production == []:
                    break
                generated += production[0]
                if len(production) > 1:
                    current = production[1]
                else:
                    current = None
                    break
            if len(generated) == length:
                return generated
        return None

    def _generate_cfg(self, length):
        max_attempts = 1000
        for _ in range(max_attempts):
            candidate = self._random_expand(self.grammar.start)
            if candidate is not None and len(candidate) == length:
                return candidate
        return None

    def _random_expand(self, symbol):
        if symbol in self.grammar.productions:
            productions = self.grammar.productions[symbol]
            production = random.choice(productions)
            result = ""
            for sym in production:
                result += self._random_expand(sym)
            return result
        else:
            return symbol