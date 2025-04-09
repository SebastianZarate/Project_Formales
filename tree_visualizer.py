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
        Muestra la imagen del árbol en el canvas.
        
        :param img_path: Ruta al archivo de imagen.
        """
        # Limpiar el canvas
        self.canvas.delete("all")
        
        # Cargar la imagen
        pil_image = Image.open(img_path)
        
        # Obtener dimensiones del canvas
        self.canvas.update_idletasks()  # Forzar actualización de geometría
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Si el canvas aún no tiene dimensiones, usar un tamaño predeterminado
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 400  # Valor predeterminado
            canvas_height = 300  # Valor predeterminado
        
        # Redimensionar la imagen si es necesario
        if pil_image.width > canvas_width or pil_image.height > canvas_height:
            ratio = min(canvas_width / pil_image.width, canvas_height / pil_image.height)
            new_width = int(pil_image.width * ratio * 0.9)  # 90% del tamaño disponible
            new_height = int(pil_image.height * ratio * 0.9)
            pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
        
        # Convertir a formato compatible con Tkinter
        self.image_tk = ImageTk.PhotoImage(pil_image)
        
        # Mostrar la imagen en el canvas
        img_item = self.canvas.create_image(
            canvas_width // 2, canvas_height // 2,
            image=self.image_tk, anchor='center'
        )
        
        # Configurar el área de desplazamiento
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
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