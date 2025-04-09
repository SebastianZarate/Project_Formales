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
        Intenta generar la cadena hasta un máximo de 1000 intentos.
        """
        max_attempts = 1000
        for _ in range(max_attempts):
            current = self.grammar.start  # Símbolo inicial
            generated = ""  # Cadena generada
            while True:
                productions = self.grammar.productions.get(current, [])  # Producciones del símbolo actual
                if not productions:
                    break  # No hay más producciones posibles
                production = self.rng.choice(productions)  # Selecciona una producción al azar
                if production == []:
                    break  # Producción vacía (ε), termina aquí
                generated += production[0]  # Agrega el símbolo terminal a la cadena
                if len(production) > 1:
                    current = production[1]  # Cambia al siguiente símbolo no terminal
                else:
                    current = None  # No hay más símbolos que procesar
                    break
            if len(generated) == length:
                return generated  # Retorna si la longitud es la deseada
        return None  # Si no se pudo generar en los intentos permitidos

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
            production = self.rng.choice(productions)  # Selecciona una producción al azar
            result = ""
            for sym in production:
                result += self._random_expand(sym)  # Expande recursivamente cada símbolo de la producción
            return result
        else:
            return symbol  # Si no hay producción, es un terminal
