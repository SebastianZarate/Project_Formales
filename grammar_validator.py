from tkinter import messagebox

# Clase que valida si una cadena pertenece a un lenguaje definido por una gramática
class GrammarValidator:
    def __init__(self, grammar):
        """
        Constructor de la clase GrammarValidator.
        Recibe una instancia de Grammar.
        """
        self.grammar = grammar

    def validate_string(self, string):
        """
        Valida la cadena según el tipo de gramática:
         - Tipo 3: gramática regular, se simula como si fuera un autómata finito.
         - Tipo 2: gramática libre de contexto, se realiza backtracking recursivo.
        
        Retorna una tupla:
         - (True, derivation, tree) si la cadena es válida.
         - (False, derivation, tree) si la cadena no es válida.
        """
        if self.grammar.type == 3:
            is_valid, derivation = self._validate_regular(string)
            # Crea un árbol simple solo si la cadena es válida
            tree = self._create_regular_tree(derivation, string) if is_valid else None
            return is_valid, derivation, tree
        elif self.grammar.type == 2:
            derivation = []
            # Árbol inicial con el símbolo de arranque
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
        """
        Valida una cadena utilizando una gramática regular simulando un autómata.
        Recorre la cadena símbolo por símbolo guiándose por las producciones.
        """
        current = self.grammar.start  # Estado inicial
        path = [current]  # Trazado de derivación
        remaining = string  # Parte de la cadena aún no procesada

        while remaining:
            char = remaining[0]  # Primer carácter a procesar
            # Filtrar producciones cuyo primer símbolo coincida con el carácter actual
            valid_options = [prod for prod in self.grammar.productions.get(current, []) if prod and prod[0] == char]
            
            if not valid_options:
                return False, path  # No hay transición válida para el carácter actual
            
            # Si estamos en la última letra de la cadena, priorizamos producciones terminales (con longitud 1)
            if len(remaining) == 1:
                production = next((prod for prod in valid_options if len(prod) == 1), valid_options[0])
            else:
                production = valid_options[0]  # En otros casos, tomamos la primera opción encontrada
            
            next_state = production[1] if len(production) > 1 else None
            path.append(f"{char} -> {next_state if next_state else 'FINAL'}")
            current = next_state
            remaining = remaining[1:]  # Avanza un carácter

        if current is None:
            return True, path  # La cadena se derivó por completo correctamente
        else:
            # Se permite una transición ε si está definida
            for prod in self.grammar.productions.get(current, []):
                if prod == []:
                    path.append("ε")
                    return True, path
            return False, path

    def _create_regular_tree(self, derivation, string):
        """
        Crea una representación de árbol de derivación para una gramática regular.
        """
        tree = {"symbol": self.grammar.start, "children": []}
        current_node = tree
        
        for i, step in enumerate(derivation[1:]):  # Se omite el primer estado inicial
            if "ε" in step:
                # Agrega un nodo para ε si es una derivación vacía
                current_node["children"].append({"symbol": "ε", "children": []})
                continue
                
            parts = step.split(" -> ")
            if len(parts) >= 1:
                symbol = parts[0]  # Símbolo terminal consumido
                next_state = parts[1] if len(parts) > 1 else "FINAL"
                
                child = {"symbol": symbol, "children": []}
                current_node["children"].append(child)
                
                if next_state != "FINAL":
                    next_node = {"symbol": next_state, "children": []}
                    child["children"].append(next_node)
                    current_node = next_node  # Se mueve al siguiente nodo

        return tree

    def _parse_cfg(self, symbol, s, derivation, tree_node):
        """
        Función recursiva que intenta derivar la cadena `s` a partir del símbolo dado.
        Usa backtracking para probar todas las producciones posibles de una CFG.
        """
        if symbol in self.grammar.productions:
            for production in self.grammar.productions[symbol]:
                step = f"{symbol} -> {' '.join(production) if production else 'ε'}"
                derivation_copy = derivation.copy()
                derivation_copy.append(step)
                
                # Crea nodos hijos para los símbolos de la producción
                prod_children = []
                for prod_sym in production:
                    prod_children.append({"symbol": prod_sym, "children": []})
                
                # Guarda el estado original del árbol
                original_children = tree_node["children"].copy()
                tree_node["children"] = prod_children
                
                remainder = s
                success = True
                
                for i, prod_sym in enumerate(production):
                    # Llama recursivamente a cada símbolo de la producción
                    result = self._parse_cfg(prod_sym, remainder, derivation_copy, prod_children[i])
                    if result is None:
                        success = False
                        break
                    else:
                        remainder = result  # Avanza en la cadena si tuvo éxito
                
                if success:
                    # Si se logró derivar toda la cadena, se actualiza la derivación final
                    derivation.clear()
                    derivation.extend(derivation_copy)
                    return remainder
                else:
                    # Si falló la producción, restaura el árbol
                    tree_node["children"] = original_children
            
            return None  # No se encontró derivación válida
        else:
            # Caso base: símbolo terminal
            if s.startswith(symbol):
                # Marca el nodo como terminal
                tree_node["symbol"] = symbol
                tree_node["terminal"] = True
                return s[len(symbol):]  # Resta el símbolo de la cadena
            else:
                return None  # No hay coincidencia
