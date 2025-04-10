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
            is_valid, transitions = self._validate_regular(string)
            # Convertir las transiciones a derivaciones detalladas paso a paso
            derivation = self._create_detailed_regular_derivation(transitions, string) if is_valid else transitions
            # Crea un árbol que refleje las derivaciones paso a paso
            tree = self._create_regular_tree(transitions, string) if is_valid else None
            return is_valid, derivation, tree
        elif self.grammar.type == 2:
            derivation = []
            # Árbol inicial con el símbolo de arranque
            tree = {"symbol": self.grammar.start, "children": []}
            result = self._parse_cfg(self.grammar.start, string, derivation, tree)
            
            # Si la validación es exitosa, creamos derivaciones detalladas
            if result is not None and result == "":
                # Formateamos las derivaciones para mostrar cada paso detalladamente
                detailed_derivation = self._create_detailed_cfg_derivation(derivation, string)
                return True, detailed_derivation, tree
            else:
                return False, derivation, None
        else:
            messagebox.showerror("Error", "Tipo de gramática no soportado para validación.")
            return False, [], None
    
    def _create_detailed_regular_derivation(self, transitions, string):
        """
        Crea una derivación detallada para gramáticas regulares mostrando cada paso
        de la aplicación de las reglas de producción.
        """
        derivation = []
        
        # Paso inicial: Mostramos el símbolo inicial
        current_form = self.grammar.start
        derivation.append(f"Inicio: {current_form}")
        
        # Reconstruir la cadena paso a paso
        pending_string = ""
        for i, transition in enumerate(transitions[1:]):  # Omitimos el primer estado (símbolo inicial)
            if "ε" in transition:
                # Caso especial: producción vacía (ε)
                rule = f"{current_form} → ε"
                derivation.append(f" {i+1}: [{rule}]")
                current_form = pending_string
                derivation.append(f": {current_form}")
                continue
            
            parts = transition.split(" -> ")
            if len(parts) >= 1:
                terminal = parts[0]  # Símbolo terminal
                next_state = parts[1] if len(parts) > 1 and parts[1] != "FINAL" else ""
                
                # Formar la regla aplicada
                if next_state:
                    rule = f"{current_form} → {terminal}{next_state}"
                else:
                    rule = f"{current_form} → {terminal}"
                
                # Mostrar la aplicación de la regla
                derivation.append(f"{i+1}: [{rule}]")
                
                # Actualizar la forma actual de la cadena
                pending_string += terminal
                current_form = next_state if next_state else ""
                
                # Mostrar el resultado después de aplicar la regla
                result = pending_string + current_form
                derivation.append(f": {result}")
        
        # Paso final: Mostrar la cadena completa verificada
        derivation.append(f"Cadena final validada: '{string}'")
        
        return derivation

    def _create_detailed_cfg_derivation(self, derivation_steps, final_string):
        """
        Crea una derivación detallada para gramáticas libres de contexto (CFG)
        mostrando cada paso de la derivación.
        """
        detailed_derivation = []
        current_form = self.grammar.start
        detailed_derivation.append(f"Inicio: {current_form}")
        
        # Reconstruir las formas sentenciales paso a paso
        for i, step in enumerate(derivation_steps):
            if " -> " in step:
                left, right = step.split(" -> ")
                
                # Buscar la primera ocurrencia del no terminal en la forma actual
                pos = current_form.find(left)
                if pos >= 0:
                    # Forma la regla aplicada
                    rule = f"{left} → {right}"
                    detailed_derivation.append(f"Paso {i+1}: Aplicar regla [{rule}] al no terminal '{left}'")
                    
                    # Aplicar la sustitución
                    replacement = right if right != "ε" else ""
                    new_form = current_form[:pos] + replacement + current_form[pos+len(left):]
                    detailed_derivation.append(f"Resultado: {new_form}")
                    
                    # Actualizar la forma actual
                    current_form = new_form
        
        # Paso final: Verificar que la forma final coincide con la cadena
        if current_form == final_string:
            detailed_derivation.append(f"Cadena final validada: '{final_string}'")
        
        return detailed_derivation

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

    def _create_regular_tree(self, transitions, string):
        """
        Crea una representación de árbol de derivación para una gramática regular
        que refleje los pasos de la derivación.
        """
        # El nodo raíz es el símbolo inicial
        tree = {"symbol": self.grammar.start, "children": [], "description": "Símbolo inicial"}
        current_node = tree
        
        # Construir el árbol según las transiciones
        for i, step in enumerate(transitions[1:]):
            if "ε" in step:
                # Caso especial: producción vacía (ε)
                current_node["children"].append({
                    "symbol": "ε", 
                    "children": [], 
                    "terminal": True,
                    "description": "Producción vacía"
                })
                continue
                
            parts = step.split(" -> ")
            if len(parts) >= 1:
                terminal = parts[0]  # Símbolo terminal
                next_state = parts[1] if len(parts) > 1 else "FINAL"
                
                # Crear nodo terminal con descripción
                terminal_node = {
                    "symbol": terminal, 
                    "children": [], 
                    "terminal": True,
                    "description": f"Terminal en posición {i}"
                }
                
                # Agregar el nodo terminal a la estructura
                current_node["children"].append(terminal_node)
                
                # Si hay un estado siguiente, agregar como hijo
                if next_state != "FINAL":
                    next_node = {
                        "symbol": next_state, 
                        "children": [],
                        "description": f"No terminal después de consumir '{terminal}'"
                    }
                    terminal_node["children"].append(next_node)
                    current_node = next_node
        
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
                for i, prod_sym in enumerate(production):
                    # Agregar descripción a cada símbolo de la producción
                    description = f"Símbolo {i+1} de la producción {symbol} → {' '.join(production)}"
                    prod_children.append({"symbol": prod_sym, "children": [], "description": description})
                
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
                    
                    # Agregar información de la producción aplicada al nodo
                    tree_node["production_applied"] = f"{symbol} → {' '.join(production) if production else 'ε'}"
                    
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
                tree_node["description"] = f"Terminal '{symbol}' coincide con la entrada"
                return s[len(symbol):]  # Resta el símbolo de la cadena
            else:
                return None  # No hay coincidencia