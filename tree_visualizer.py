import graphviz
import tempfile
import os
from tkinter import messagebox, Scrollbar, Canvas, Frame
from PIL import Image, ImageTk

class TreeVisualizer:
    """
    Clase para visualizar árboles de derivación usando Graphviz.
    """
    def __init__(self, canvas_frame):
        """
        Inicializa el visualizador con el frame donde se mostrará el árbol con barras de desplazamiento.
        
        :param canvas_frame: Frame de Tkinter donde se colocará el canvas con barras de desplazamiento.
        """
        self.canvas_frame = canvas_frame
        
        # Crear canvas y barras de desplazamiento
        self.canvas = Canvas(canvas_frame, bg='white')
        self.h_scrollbar = Scrollbar(canvas_frame, orient='horizontal', command=self.canvas.xview)
        self.v_scrollbar = Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        
        # Configurar el canvas para usar las barras de desplazamiento
        self.canvas.config(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        
        # Colocar los elementos en el frame usando grid para un mejor control del layout
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.h_scrollbar.grid(row=1, column=0, sticky='ew')
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Configurar el frame para que se expanda con la ventana
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Variables para almacenar referencias a objetos
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
        
        :param tree_data: Diccionario con la estructura del árbol.
        :param grammar: Instancia de Grammar para distinguir terminales y no terminales.
        :return: True si el árbol se creó correctamente, False en caso contrario.
        """
        try:            
            # Crear un nuevo grafo dirigido
            os.environ["PATH"] = r'C:\Program Files\Graphviz\bin' + os.pathsep + os.environ["PATH"]
        
            # Crear un nuevo grafo dirigido
            self.graph = graphviz.Digraph(format='png', engine='dot')
            self.graph.attr(rankdir='LR', splines='ortho', nodesep='0.3', 
                        ranksep='0.5', fontname='Arial')
            
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
        
        :param node_data: Diccionario con datos del nodo.
        :param parent_id: ID del nodo padre.
        :param grammar: Instancia de Grammar.
        :param node_counter: Contador para generar IDs únicos.
        :return: ID del nodo creado.
        """
        # Generar ID único para este nodo
        node_id = f"node_{node_counter[0]}"
        node_counter[0] += 1
        
        # Determinar si es un terminal o no terminal
        symbol = node_data["symbol"]
        is_terminal = node_data.get("terminal", False) or (
            symbol not in grammar.productions and 
            symbol not in [None, "ε"]
        )
        
        # Establecer atributos según el tipo de nodo
        if is_terminal:
            self.graph.node(node_id, label=symbol, shape='box', 
                         style='filled', fillcolor='#f0a500', fontcolor='white')
        elif symbol == "ε":
            self.graph.node(node_id, label="ε", shape='box', 
                         style='filled', fillcolor='#90ee90', fontcolor='black')
        else:
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
        Muestra la imagen del árbol en el canvas con un tamaño 3 veces mayor
        y configurado para permitir scroll.
        
        :param img_path: Ruta al archivo de imagen.
        """
        # Limpiar el canvas
        self.canvas.delete("all")
        
        # Cargar la imagen
        pil_image = Image.open(img_path)
        
        # Calcular dimensiones 3 veces más grandes que las originales
        new_width = pil_image.width * 1
        new_height = pil_image.height * 1
        
        # Redimensionar la imagen al tamaño aumentado
        pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
        
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