from tkinter import messagebox
import random

# Clase que se encarga de generar cadenas que pertenecen a una gramática dada
class GrammarGenerator:
    def __init__(self, grammar):
        """
        Constructor de la clase GrammarGenerator.
        Recibe una instancia de Grammar y configura un generador aleatorio.
        """
        self.grammar = grammar
        self.rng = random.Random()  # Crea un generador de números aleatorios independiente
        self.rng.seed()  # Inicializa la semilla con el tiempo actual (por defecto)

    def generate_string(self, length):
        """
        Genera una cadena que pertenece a la gramática y que tenga la longitud exacta indicada.
        Soporta gramáticas de tipo 2 (CFG) y tipo 3 (Regulares).
        """
        if self.grammar.type == 3:
            return self._generate_regular(length)  # Usa el generador para gramáticas regulares
        elif self.grammar.type == 2:
            return self._generate_cfg(length)  # Usa el generador para gramáticas libres de contexto
        else:
            # Muestra un error si el tipo de gramática no está soportado
            messagebox.showerror("Error", "Tipo de gramática no soportado para generación.")
            return None

    def _generate_regular(self, length):
        """
        Genera una cadena de una gramática regular que tenga la longitud exacta indicada.
        Versión corregida para generar cadenas válidas y consistentes con el validador.
        """
        max_attempts = 1000
        for _ in range(max_attempts):
            current = self.grammar.start  # Símbolo inicial
            generated = ""  # Cadena generada
            transitions = []  # Registrar transiciones para debugging
            
            # Intentamos generar una cadena de la longitud deseada
            while len(generated) < length and current is not None:
                productions = self.grammar.productions.get(current, [])
                
                if not productions:
                    # No hay producciones para este símbolo no terminal
                    break
                
                valid_productions = []
                for prod in productions:
                    # Filtramos producciones para evitar generar cadenas demasiado largas
                    if not prod:  # Es epsilon
                        if len(generated) == length:
                            valid_productions.append(prod)
                    else:
                        # Para producciones no vacías, verificamos que no excedamos la longitud
                        remaining_length = length - len(generated)
                        if remaining_length >= 1:  # Necesitamos al menos 1 espacio para el terminal
                            valid_productions.append(prod)
                
                if not valid_productions:
                    # No hay producciones válidas para la longitud deseada
                    break
                
                # Elegimos una producción aleatoria de las válidas
                production = self.rng.choice(valid_productions)
                
                # Aplicamos la producción
                if production:  # No es epsilon
                    generated += production[0]  # Añadimos el terminal
                    transitions.append(f"{current} -> {production[0]}" + 
                                      (f" {production[1]}" if len(production) > 1 else ""))
                    
                    # Actualizamos el símbolo no terminal actual
                    current = production[1] if len(production) > 1 else None
                else:  # Es epsilon
                    transitions.append(f"{current} -> ε")
                    break
            
            # Verificamos si la cadena generada tiene la longitud exacta
            if len(generated) == length:
                # Si terminamos sin un estado actual o si el estado actual puede aceptar
                # la cadena vacía, entonces la cadena generada es válida
                if current is None:
                    return generated
                
                # Verificamos si el estado actual tiene una producción vacía
                if current and any(not prod for prod in self.grammar.productions.get(current, [])):
                    return generated
                
                # Verificamos si el estado actual tiene producciones que solo consumen un terminal
                # (sin pasar a otro estado)
                if current:
                    for prod in self.grammar.productions.get(current, []):
                        if len(prod) == 1 and prod[0] in self.grammar.terminals:
                            return generated
            
        # Si no pudimos generar una cadena válida después de muchos intentos
        return None

    def _generate_cfg(self, length):
        """
        Genera una cadena de una gramática libre de contexto (tipo 2) de longitud exacta.
        Usa expansión aleatoria desde el símbolo inicial.
        """
        max_attempts = 5000  # Mayor cantidad de intentos debido a la complejidad
        for _ in range(max_attempts):
            candidate = self._random_expand(self.grammar.start)  # Intenta expandir el símbolo inicial
            if candidate is not None and len(candidate) == length:
                return candidate.replace(" ", "")  # Elimina espacios si los hay (opcional)
        return None  # No se encontró una cadena válida

    def _random_expand(self, symbol):
        """
        Expande recursivamente un símbolo de forma aleatoria usando las producciones de la gramática.
        Si el símbolo no tiene producciones, se considera un terminal y se retorna tal cual.
        """
        if symbol in self.grammar.productions:
            productions = self.grammar.productions[symbol]  # Producciones disponibles para el símbolo
            if not productions:
                return ""  # Producción vacía (epsilon)
                
            production = self.rng.choice(productions)  # Selecciona una producción al azar
            
            if not production:  # Es epsilon
                return ""
                
            result = ""
            for sym in production:
                expanded = self._random_expand(sym)  # Expande recursivamente cada símbolo de la producción
                if expanded is not None:
                    result += expanded
                else:
                    return None  # Si algún símbolo no se puede expandir, retorna None
            return result
        else:
            return symbol  # Si no hay producción, es un terminal