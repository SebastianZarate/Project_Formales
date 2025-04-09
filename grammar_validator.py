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
        Retorna (True, derivation, tree) si es válida o (False, derivation, tree) en caso contrario.
        """
        if self.grammar.type == 3:
            is_valid, derivation = self._validate_regular(string)
            # Para gramáticas tipo 3, usaremos una estructura simple de árbol
            tree = self._create_regular_tree(derivation, string) if is_valid else None
            return is_valid, derivation, tree
        elif self.grammar.type == 2:
            derivation = []
            tree = {"symbol": self.grammar.start, "children": []}
            result = self._parse_cfg(self.grammar.start, string, derivation, tree)
            if result is not None and result == "":
                return True, derivation, tree
            else:
                return False, derivation, None
        else:
            messagebox.showerror("Error", "Tipo de gramática no soportado para validación.")
            return False, [], None

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

    def _create_regular_tree(self, derivation, string):
        """
        Crea una estructura de árbol simple para gramáticas regulares.
        """
        tree = {"symbol": self.grammar.start, "children": []}
        current_node = tree
        
        for i, step in enumerate(derivation[1:]):  # Skip the first state
            if "ε" in step:
                current_node["children"].append({"symbol": "ε", "children": []})
                continue
                
            parts = step.split(" -> ")
            if len(parts) >= 1:
                symbol = parts[0]
                next_state = parts[1] if len(parts) > 1 else "FINAL"
                
                child = {"symbol": symbol, "children": []}
                current_node["children"].append(child)
                
                if next_state != "FINAL":
                    next_node = {"symbol": next_state, "children": []}
                    child["children"].append(next_node)
                    current_node = next_node
        
        return tree

    def _parse_cfg(self, symbol, s, derivation, tree_node):
        if symbol in self.grammar.productions:
            for production in self.grammar.productions[symbol]:
                step = f"{symbol} -> {' '.join(production) if production else 'ε'}"
                derivation_copy = derivation.copy()
                derivation_copy.append(step)
                
                # Create tree node for this production
                prod_children = []
                for prod_sym in production:
                    prod_children.append({"symbol": prod_sym, "children": []})
                
                # Save the original tree structure
                original_children = tree_node["children"].copy()
                tree_node["children"] = prod_children
                
                remainder = s
                success = True
                
                for i, prod_sym in enumerate(production):
                    result = self._parse_cfg(prod_sym, remainder, derivation_copy, prod_children[i])
                    if result is None:
                        success = False
                        break
                    else:
                        remainder = result
                
                if success:
                    derivation.clear()
                    derivation.extend(derivation_copy)
                    return remainder
                else:
                    # Restore original tree structure on failure
                    tree_node["children"] = original_children
            
            return None
        else:
            # Terminal symbol
            if s.startswith(symbol):
                # For terminal symbols, no children
                tree_node["symbol"] = symbol
                tree_node["terminal"] = True
                return s[len(symbol):]
            else:
                return None