from tkinter import messagebox

class GrammarValidator:
    def __init__(self, grammar):
        """
        Recibe una instancia de Grammar.
        """
        self.grammar = grammar

    def validate_string(self, string):
        """
        Valida la cadena según el tipo de gramática:
         - Tipo 3: se asume gramática regular y se simula un autómata.
         - Tipo 2: se realiza un análisis recursivo (backtracking) para gramáticas CFG.
        Retorna (True, derivation) si es válida o (False, derivation) en caso contrario.
        """
        if self.grammar.type == 3:
            return self._validate_regular(string)
        elif self.grammar.type == 2:
            derivation = []
            result = self._parse_cfg(self.grammar.start, string, derivation)
            if result is not None and result == "":
                return True, derivation
            else:
                return False, derivation
        else:
            messagebox.showerror("Error", "Tipo de gramática no soportado para validación.")
            return False, []

    def _validate_regular(self, string):
        current = self.grammar.start
        path = [current]
        remaining = string

        while remaining:
            char = remaining[0]
            found = False
            for production in self.grammar.productions.get(current, []):
                if len(production) >= 1 and production[0] == char:
                    next_state = production[1] if len(production) > 1 else None
                    found = True
                    path.append(f"{char} -> {next_state if next_state else 'FINAL'}")
                    current = next_state
                    remaining = remaining[1:]
                    break
            if not found:
                return False, path

        if current is None:
            return True, path
        else:
            # Se permite producción epsilon en el estado final
            for prod in self.grammar.productions.get(current, []):
                if prod == []:
                    path.append("ε")
                    return True, path
            return False, path

    def _parse_cfg(self, symbol, s, derivation):
        if symbol in self.grammar.productions:
            for production in self.grammar.productions[symbol]:
                step = f"{symbol} -> {' '.join(production) if production else 'ε'}"
                derivation_copy = derivation.copy()
                derivation_copy.append(step)
                remainder = s
                success = True
                for prod_sym in production:
                    result = self._parse_cfg(prod_sym, remainder, derivation_copy)
                    if result is None:
                        success = False
                        break
                    else:
                        remainder = result
                if success:
                    derivation.clear()
                    derivation.extend(derivation_copy)
                    return remainder
            return None
        else:
            if s.startswith(symbol):
                return s[len(symbol):]
            else:
                return None
