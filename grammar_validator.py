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
        Versión corregida para manejar correctamente gramáticas regulares.
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

        # Iniciamos la simulación
        while remaining and current is not None:
            char = remaining[0]
            valid_transitions = []
            
            # Buscamos todas las transiciones posibles para el estado actual y el siguiente símbolo
            for prod in self.grammar.productions.get(current, []):
                if prod and prod[0] == char:
                    next_state = prod[1] if len(prod) > 1 else None
                    valid_transitions.append((prod[0], next_state))
            
            # Si no hay transiciones válidas, la cadena no es aceptada
            if not valid_transitions:
                return False, path
            
            # Tomamos la primera transición (se podría implementar backtracking para todas)
            terminal, next_state = valid_transitions[0]
            
            # Registramos la transición
            transition_info = f"{terminal} -> {next_state}" if next_state else f"{terminal} -> FINAL"
            path.append(transition_info)
            
            # Avanzamos al siguiente estado y consumimos el símbolo
            current = next_state
            remaining = remaining[1:]
        
        # Una vez procesada toda la cadena, verificamos si estamos en un estado final
        if not remaining:
            # Si no hay más símbolos por consumir, hemos aceptado la cadena si:
            # 1. No hay estado actual (transición a FINAL), o
            # 2. El estado actual acepta la cadena vacía
            if current is None:
                return True, path
            
            # Verificamos si el estado actual tiene una producción vacía o terminal
            for prod in self.grammar.productions.get(current, []):
                if not prod or (len(prod) == 1 and prod[0] in self.grammar.terminals):
                    path.append("ε")
                    return True, path
        
        # Si llegamos aquí, la cadena no es aceptada
        return False, path

    def _create_regular_tree(self, transitions, string):
        """
        Construye un árbol de derivación para una gramática regular a partir de las transiciones.
        Versión corregida para crear un árbol más claro y completo.
        """
        if not transitions or len(transitions) <= 1:
            return None
        
        # Creamos el nodo raíz con el símbolo inicial
        tree = {"symbol": self.grammar.start, "children": [], "description": "Símbolo inicial"}
        current_node = tree
        
        # Procesamos todas las transiciones para construir el árbol
        for i, step in enumerate(transitions[1:]):
            if "ε" in step:
                # Caso de producción vacía
                current_node["children"].append({
                    "symbol": "ε",
                    "children": [],
                    "terminal": True,
                    "description": "Producción vacía"
                })
                continue
            
            # Extraemos la información de la transición
            parts = step.split(" -> ")
            terminal = parts[0].strip()
            next_state = parts[1].strip() if len(parts) > 1 and parts[1] != "FINAL" else None
            
            # Creamos un nodo para el terminal
            terminal_node = {
                "symbol": terminal,
                "children": [],
                "terminal": True,
                "description": f"Terminal '{terminal}'"
            }
            
            # Añadimos el nodo terminal como hijo del nodo actual
            current_node["children"].append(terminal_node)
            
            # Si hay un estado siguiente, creamos un nodo para él
            if next_state:
                next_node = {
                    "symbol": next_state,
                    "children": [],
                    "description": f"No terminal '{next_state}'"
                }
                # El nuevo estado es hijo del terminal
                terminal_node["children"].append(next_node)
                # Actualizamos el nodo actual para seguir construyendo desde ahí
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