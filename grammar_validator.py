from tkinter import messagebox

# Clase que valida si una cadena pertenece a un lenguaje definido por una gramática
class GrammarValidator:
    def __init__(self, grammar):
        """
        Constructor de la clase GrammarValidator.
        Recibe una instancia de Grammar que contiene el tipo, producciones y símbolo inicial.
        """
        self.grammar = grammar

    def validate_string(self, string):
        """
        Valida la cadena según el tipo de gramática:
         - Tipo 3: gramática regular, se simula como un autómata finito.
         - Tipo 2: gramática libre de contexto, se realiza backtracking recursivo.

        Retorna una tupla:
         - (True, derivation, tree) si la cadena es válida.
         - (False, derivation, tree) si la cadena no es válida.
        """
        if self.grammar.type == 3:
            # Validación para gramática regular (tipo 3)
            is_valid, transitions = self._validate_regular(string)
            derivation = self._create_detailed_regular_derivation(transitions, string) if is_valid else transitions
            tree = self._create_regular_tree(transitions, string) if is_valid else None
            return is_valid, derivation, tree
        elif self.grammar.type == 2:
            # Validación para gramática libre de contexto (tipo 2)
            derivation = []
            tree = {"symbol": self.grammar.start, "children": [], "description": "Símbolo inicial"}
            result = self._parse_cfg(self.grammar.start, string, derivation, tree, 0, set())
            
            if result is not None and result == "":
                detailed_derivation = self._create_detailed_cfg_derivation(derivation, string)
                return True, detailed_derivation, tree
            else:
                return False, derivation, None
        else:
            # Caso de tipo de gramática no soportado
            messagebox.showerror("Error", "Tipo de gramática no soportado para validación.")
            return False, [], None

    def _create_detailed_regular_derivation(self, transitions, string):
        """
        Crea una derivación paso a paso detallada para gramáticas regulares.
        """
        derivation = []
        current_form = self.grammar.start
        derivation.append(f"Inicio: {current_form}")
        pending_string = ""

        for i, transition in enumerate(transitions[1:]):
            if "ε" in transition:
                # Producción vacía
                rule = f"{current_form} → ε"
                derivation.append(f" {i+1}: [{rule}]")
                current_form = pending_string
                derivation.append(f": {current_form}")
                continue

            parts = transition.split(" -> ")
            terminal = parts[0]
            next_state = parts[1] if len(parts) > 1 and parts[1] != "FINAL" else ""

            rule = f"{current_form} → {terminal}{next_state}" if next_state else f"{current_form} → {terminal}"
            derivation.append(f"{i+1}: [{rule}]")
            pending_string += terminal
            current_form = next_state
            derivation.append(f": {pending_string + current_form}")

        derivation.append(f"Cadena final validada: '{string}'")
        return derivation

    def _create_detailed_cfg_derivation(self, derivation_steps, final_string):
        """
        Crea una derivación paso a paso para gramáticas libres de contexto.
        """
        detailed_derivation = []
        current_form = self.grammar.start
        detailed_derivation.append(f"Inicio: {current_form}")

        for i, step in enumerate(derivation_steps):
            if " -> " in step:
                left, right = step.split(" -> ")
                pos = current_form.find(left)
                if pos >= 0:
                    rule = f"{left} → {right}"
                    detailed_derivation.append(f" {i+1}:  [{rule}]  '{left}'")
                    replacement = right if right != "ε" else ""
                    current_form = current_form[:pos] + replacement + current_form[pos+len(left):]
                    detailed_derivation.append(f": {current_form}")

        if current_form == final_string:
            detailed_derivation.append(f"Cadena final validada: '{final_string}'")
        return detailed_derivation

    def _validate_regular(self, string):
        """
        Simula la validación de una gramática regular como si fuera un autómata.
        Versión corregida para manejar correctamente los estados finales.
        """
        current = self.grammar.start
        path = [current]
        remaining = string

        # Si la cadena está vacía, verificamos si el símbolo inicial acepta producción vacía
        if not string:
            for prod in self.grammar.productions.get(current, []):
                if not prod:  # producción vacía (epsilon)
                    path.append("ε")
                    return True, path
            return False, path

        while remaining:
            char = remaining[0]
            valid_options = [prod for prod in self.grammar.productions.get(current, []) if prod and prod[0] == char]

            if not valid_options:
                return False, path

            # Escoge la primera opción válida
            production = valid_options[0]
            
            # Registra la transición en el camino
            next_state = production[1] if len(production) > 1 else None
            path.append(f"{char} -> {next_state if next_state else 'FINAL'}")
            
            # Actualiza el estado actual y la cadena restante
            current = next_state
            remaining = remaining[1:]

        # Cuando se ha consumido toda la cadena, verificamos si estamos en un estado final
        # Un estado es final si:
        # 1. No hay más estados (current es None), o
        # 2. El estado actual tiene una producción vacía (epsilon), o
        # 3. El estado actual tiene producciones que terminan sin pasar a otro estado
        
        if current is None:
            # Si terminamos sin un estado actual, es válido
            return True, path
        else:
            # Si hay un estado actual, verificamos si es un estado final
            productions = self.grammar.productions.get(current, [])
            
            # Caso 1: El estado tiene una producción vacía (epsilon)
            for prod in productions:
                if not prod:  # producción vacía
                    path.append("ε")
                    return True, path
            
            # Caso 2: El estado tiene producciones que terminan (producciones de un solo símbolo terminal)
            for prod in productions:
                if len(prod) == 1 and prod[0] in self.grammar.terminals:
                    # No consumimos este símbolo pero confirmamos que el estado es final
                    return True, path
            
            # Si llegamos aquí, no es un estado final válido
            return False, path

    def _create_regular_tree(self, transitions, string):
        """
        Construye un árbol de derivación para una gramática regular a partir de las transiciones.
        """
        tree = {"symbol": self.grammar.start, "children": [], "description": "Símbolo inicial"}
        current_node = tree

        for i, step in enumerate(transitions[1:]):
            if "ε" in step:
                current_node["children"].append({
                    "symbol": "ε",
                    "children": [],
                    "terminal": True,
                    "description": "Producción vacía"
                })
                continue

            parts = step.split(" -> ")
            terminal = parts[0]
            next_state = parts[1] if len(parts) > 1 and parts[1] != "FINAL" else "FINAL"

            terminal_node = {
                "symbol": terminal,
                "children": [],
                "terminal": True,
                "description": f"Terminal en posición {i}"
            }

            current_node["children"].append(terminal_node)

            if next_state != "FINAL":
                next_node = {
                    "symbol": next_state,
                    "children": [],
                    "description": f"No terminal después de consumir '{terminal}'"
                }
                terminal_node["children"].append(next_node)
                current_node = next_node

        return tree

    def _parse_cfg(self, symbol, s, derivation, tree_node, recursion_depth=0, visited=None):
        """
        Valida una cadena usando backtracking sobre una gramática libre de contexto.
        """
        if recursion_depth > 100:
            return None  # Evitar recursión infinita

        if visited is None:
            visited = set()

        visit_key = (symbol, s)
        if visit_key in visited:
            return None

        visited.add(visit_key)

        if symbol in self.grammar.productions:
            for production in self.grammar.productions[symbol]:
                step = f"{symbol} -> {' '.join(production) if production else 'ε'}"
                derivation_copy = derivation.copy()
                derivation_copy.append(step)

                prod_children = []
                for i, prod_sym in enumerate(production):
                    description = f"Símbolo {i+1} de la producción {symbol} → {' '.join(production)}"
                    prod_children.append({"symbol": prod_sym, "children": [], "description": description})

                original_children = tree_node["children"].copy()
                tree_node["children"] = prod_children

                remainder = s
                success = True

                if not production:
                    if not s:
                        derivation.clear()
                        derivation.extend(derivation_copy)
                        tree_node["production_applied"] = f"{symbol} → ε"
                        return ""
                    else:
                        tree_node["children"] = original_children
                        continue

                for i, prod_sym in enumerate(production):
                    new_visited = visited.copy()
                    result = self._parse_cfg(prod_sym, remainder, derivation_copy,
                                             prod_children[i], recursion_depth + 1, new_visited)
                    if result is None:
                        success = False
                        break
                    elif len(result) == len(remainder):
                        if i < len(production) - 1:
                            success = False
                            break
                    remainder = result

                if success:
                    derivation.clear()
                    derivation.extend(derivation_copy)
                    tree_node["production_applied"] = f"{symbol} → {' '.join(production) if production else 'ε'}"
                    return remainder
                else:
                    tree_node["children"] = original_children

            return None
        else:
            # Caso terminal: se compara directamente con el string restante
            if s.startswith(symbol):
                tree_node["symbol"] = symbol
                tree_node["terminal"] = True
                tree_node["description"] = f"Terminal '{symbol}' coincide con la entrada"
                return s[len(symbol):]
            else:
                return None