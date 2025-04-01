# Módulo de Análisis de Gramáticas Tipo 2 y Tipo 3

## Descripción
Este proyecto consiste en un módulo capaz de leer gramáticas de Tipo 2 y Tipo 3, permitiendo:
- Evaluar si una cadena ingresada pertenece al lenguaje definido por la gramática, mostrando los caminos posibles.
- Generar cadenas que pertenecen al lenguaje con una longitud determinada por el usuario.

## Características
- **Compatibilidad con gramáticas de Tipo 2 y Tipo 3:** Soporte para gramáticas independientes del contexto y regulares.
- **Evaluación de cadenas:** Verifica si una cadena pertenece al lenguaje de la gramática y muestra el proceso.
- **Generación de cadenas:** Permite generar palabras válidas de longitud n en el lenguaje definido.

## Requisitos
- Lenguaje de programación: Python (3.x)
- Librerías necesarias: tkinter, ttk

## Instalación
1. Clonar el repositorio:
   ```sh
   git clone [https://github.com/SebastianZarate/Project_Formales.git]
   ```
2. Instalar dependencias:
   ```sh
   [pip install ""]
   ```
3. Ejecutar el módulo:
   ```sh
   [python GrammarProcessor.py]
   ```
## Instrucciones de uso
- Subir un archivo de formato .grm, como por ejemplo, el siguiente formato:
-  ```sh
   [type: 2 o 3
    start: S
    S -> a B | b A | ε
    A -> a S | b A A
    B -> b S | a B B]
   ```
## Funcionalidades:

Cargar gramática: Botón "Cargar Gramática"

Validar cadena: Pestaña "Validar Cadena", ingresar cadena y click en Validar

Generar cadena: Pestaña "Generar Cadena", seleccionar longitud y click en Generar
   




