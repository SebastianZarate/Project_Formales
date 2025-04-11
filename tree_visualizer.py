import graphviz
import tempfile
import os
from tkinter import messagebox
from PIL import Image, ImageTk

class TreeVisualizer:
    """
    Clase para visualizar árboles de derivación usando Graphviz.
    """
    def __init__(self, canvas):
        """
        Inicializa el visualizador con el canvas donde se mostrará el árbol.
        
        :param canvas: Canvas de Tkinter donde se mostrará el árbol.
        """
        self.canvas = canvas
        self.graph = None
        self.image = None
        self.image_tk = None
        self.temp_files = []
        
        # Configurar eventos para zoom con rueda del ratón
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)  # Windows
        self.canvas.bind("<Button-4>", self._on_mousewheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_mousewheel)    # Linux scroll down
    
    def _on_mousewheel(self, event):
        """
        Maneja el evento de la rueda del ratón para hacer scroll vertical.
        """
        if event.num == 4 or event.delta > 0:
            # Scroll hacia arriba
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            # Scroll hacia abajo
            self.canvas.yview_scroll(1, "units")
    
    def create_tree(self, tree_data, grammar):
        """
        Crea un árbol de derivación usando Graphviz.
        Versión mejorada para manejar mejor las gramáticas tipo 3.
        
        :param tree_data: Diccionario con la estructura del árbol.
        :param grammar: Instancia de Grammar para distinguir terminales y no terminales.
        :return: True si el árbol se creó correctamente, False en caso contrario.
        """
        try:
            # Verificar si Graphviz está instalado
            try:
                os.environ["PATH"] = r'C:\Program Files\Graphviz\bin' + os.pathsep + os.environ["PATH"]
            except Exception:
                # Ignorar errores si la ruta no existe
                pass
            
            # Crear un nuevo grafo dirigido
            self.graph = graphviz.Digraph(format='png', engine='dot')
            
            # Configurar atributos del grafo según el tipo de gramática
            if grammar.type == 3:  # Gramática regular
                self.graph.attr(rankdir='LR', nodesep='0.3', ranksep='0.5', fontname='Arial')
            else:  # Gramática tipo 2 (CFG)
                self.graph.attr(rankdir='TB', nodesep='0.3', ranksep='0.5', fontname='Arial')
            
            # Generar el árbol recursivamente
            self._add_node(tree_data, None, grammar)
            
            # Crear un archivo temporal para la imagen
            temp_dir = tempfile.gettempdir()
            img_path = os.path.join(temp_dir, 'derivation_tree.png')
            self.temp_files.append(img_path)
            
            # Renderizar y verificar que la imagen existe
            self.graph.render(filename='derivation_tree', directory=temp_dir, cleanup=True, view=False)
            
            # Verificar que se creó la imagen
            render_path = os.path.join(temp_dir, 'derivation_tree.png')
            if not os.path.exists(render_path) or os.path.getsize(render_path) == 0:
                messagebox.showerror("Error", "La imagen del árbol no se generó correctamente")
                return False
            
            # Cargar la imagen en el canvas
            self.display_image(img_path)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear el árbol: {str(e)}")
            return False
    
    def _add_node(self, node_data, parent_id, grammar, node_counter=[0]):
        """
        Añade un nodo al grafo de forma recursiva.
        Versión mejorada para manejar mejor los nodos terminales y no terminales.
        
        :param node_data: Diccionario con datos del nodo.
        :param parent_id: ID del nodo padre.
        :param grammar: Instancia de Grammar.
        :param node_counter: Contador para generar IDs únicos.
        :return: ID del nodo creado.
        """
        # Generar ID único para este nodo
        node_id = f"node_{node_counter[0]}"
        node_counter[0] += 1
        
        # Extraer información del nodo
        symbol = node_data["symbol"]
        is_terminal = node_data.get("terminal", False)
        
        # Si no está explícitamente marcado como terminal, verificamos si es un terminal
        if not is_terminal and symbol not in grammar.nonterminals and symbol not in [None, "ε"]:
            is_terminal = True
        
        # Establecer atributos del nodo según su tipo
        if symbol == "ε":
            # Nodo épsilon
            self.graph.node(node_id, label="ε", shape='box', 
                         style='filled', fillcolor='#90ee90', fontcolor='black')
        elif is_terminal:
            # Nodo terminal
            self.graph.node(node_id, label=symbol, shape='box', 
                         style='filled', fillcolor='#f0a500', fontcolor='white')
        else:
            # Nodo no terminal
            self.graph.node(node_id, label=symbol, shape='ellipse', 
                         style='filled', fillcolor='#4a6ea9', fontcolor='white')
        
        # Conectar con el nodo padre
        if parent_id is not None:
            self.graph.edge(parent_id, node_id)
        
        # Procesar nodos hijos
        if "children" in node_data and node_data["children"]:
            for child in node_data["children"]:
                self._add_node(child, node_id, grammar, node_counter)
        
        return node_id
    
    def display_image(self, img_path):
        """
        Muestra la imagen del árbol en el canvas con un tamaño apropiado
        y configurado para permitir scroll.
        
        :param img_path: Ruta al archivo de imagen.
        """
        # Limpiar el canvas
        self.canvas.delete("all")
        
        # Cargar la imagen
        pil_image = Image.open(img_path)
        
        # Mantener el tamaño original para mejor claridad
        new_width = pil_image.width
        new_height = pil_image.height
        
        # Convertir a formato compatible con Tkinter
        self.image_tk = ImageTk.PhotoImage(pil_image)
        
        # Configurar el área de desplazamiento para acomodar toda la imagen
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))
        
        # Mostrar la imagen en el canvas desde la esquina superior izquierda
        img_item = self.canvas.create_image(
            0, 0,
            image=self.image_tk, anchor='nw'
        )
    
    def cleanup(self):
        """
        Limpia los archivos temporales generados.
        """
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
        self.temp_files = []