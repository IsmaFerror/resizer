#!/usr/bin/env python3

# --- 1. IMPORTS (Todo al principio) ---
import os
import io
import threading
import queue
import requests
from PIL import Image
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog

# --- 2. FUNCIONES DE LÓGICA (Aquí es donde van) ---
# Estas son las funciones del archivo "standalone_functions.py"

HEADERS = {"User-Agent": "resizer-downloader-gui/1.0"}
TIMEOUT = 15

def fetch_image(url):
    """Descarga los bytes de una imagen desde una URL."""
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.content

def resize_and_save(image_bytes, out_path, final_size):
    """Redimensiona y guarda la imagen con fondo transparente."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    
    # Usa thumbnail para mantener el aspect ratio
    img.thumbnail(final_size, Image.LANCZOS)
    
    # Crea un lienzo transparente del tamaño final
    background = Image.new("RGBA", final_size, (0, 0, 0, 0))
    
    # Calcula la posición para centrar la imagen
    x = (final_size[0] - img.width) // 2
    y = (final_size[1] - img.height) // 2
    
    # Pega la imagen redimensionada en el centro del lienzo
    background.paste(img, (x, y), img)
    
    # Asegura que el directorio de salida exista
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    # Guarda la imagen final como PNG
    background.save(out_path, format="PNG", optimize=True)

def process_image_entry(name, url, output_dir, final_size):
    """
    Procesa una sola imagen (descarga, redimensiona, guarda).
    Devuelve un mensaje de estado en lugar de imprimir.
    """
    try:
        image_bytes = fetch_image(url)
    except Exception as e:
        return f"❌ Error al descargar '{name}': {e}"
    
    # Crea un nombre de archivo seguro
    safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in name)
    out_path = os.path.join(output_dir, f"{safe_name}.png")
    
    try:
        resize_and_save(image_bytes, out_path, final_size)
    except Exception as e:
        return f"❌ Error al procesar '{name}': {e}"
        
    return f"✅ Guardada: {name} en {out_path}"


# --- 3. LA CLASE PRINCIPAL (Después de las funciones) ---
# Esta es la clase del archivo "resizer_app_class.py"

class ResizerApp(ttk.Window):
    
    def __init__(self):
        # 1. Iniciar la ventana con el tema "darkly" (fondo negro)
        super().__init__(themename="darkly", title="Redimensionador de Imágenes")

        # --- CORRECCIÓN DE RUTA DEL ICONO ---
        try:
            # Construye la ruta absoluta al icono
            base_path = os.path.dirname(os.path.abspath(__file__))
            # Asegúrate de que tu icono se llama "world.ico" o cámbialo
            icon_path = os.path.join(base_path, "world.ico") 
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Error al cargar el icono: {e}")
            # Si falla, la app continúa sin icono
        # --- FIN DE LA CORRECCIÓN ---

        self.geometry("800x600")
        self.resizable(False, False)
        
        # Diccionario "traductor": Nombre Bonito -> Nombre Real 
        self.theme_map = {
            "Dark": "darkly",      # Tu nombre "Dark" se traduce a "darkly"
            "Blue": "superhero",   # "Blue" se traduce a "superhero"
            "Light": "litera"      # "Light" se traduce a "litera"
        }
        
        # APLICA LOS ESTILOS MORADOS AL TEMA INICIAL
        self.apply_custom_styles() 
        
        # 2. Cola para comunicación entre hilos (¡UNA SOLA VEZ!)
        self.log_queue = queue.Queue()
        
        # 3. Variable para rastrear el estado (¡UNA SOLA VEZ!)
        self.is_processing = False

        # 4. Construir la interfaz (¡UNA SOLA VEZ!)
        self.create_widgets()
        
        # 5. Iniciar el "oyente" de la cola de logs (¡UNA SOLA VEZ!)
        self.poll_log_queue()
        
    def apply_custom_styles(self):
        """Aplica los estilos morados personalizados al tema actual."""
        
        # 1. Define tu color morado
        MY_PURPLE = '#9B59B6'
        HOVER_PURPLE = '#8E44AD' # Un morado un poco más oscuro

        # 2. Configurar los estilos "Primary"
        
        # Para botones sólidos (como "Examinar..." y "Iniciar Proceso")
        self.style.configure('Primary.TButton', 
                             background=MY_PURPLE, 
                             bordercolor=MY_PURPLE,
                             lightcolor=MY_PURPLE,
                             darkcolor=MY_PURPLE)
        # Configura el color al pasar el ratón (hover)
        self.style.map('Primary.TButton',
                       background=[('hover', HOVER_PURPLE), 
                                   ('pressed', '!disabled', HOVER_PURPLE)],
                       bordercolor=[('hover', HOVER_PURPLE), 
                                    ('pressed', '!disabled', HOVER_PURPLE)])
                       
        # Para botones de contorno (si quisieras usar alguno)
        self.style.configure('Primary.Outline.TButton', 
                             foreground=MY_PURPLE, 
                             bordercolor=MY_PURPLE)
        # Configura el color al pasar el ratón (hover)
        self.style.map('Primary.Outline.TButton',
                       foreground=[('hover', HOVER_PURPLE), 
                                   ('pressed', '!disabled', HOVER_PURPLE)],
                       bordercolor=[('hover', HOVER_PURPLE), 
                                    ('pressed', '!disabled', HOVER_PURPLE)])
    
    
    def create_widgets(self):
        """Crea y posiciona todos los elementos de la interfaz."""
        
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=BOTH, expand=YES)

        # --- SECCIÓN DE CONFIGURACIÓN ---
        config_frame = ttk.Labelframe(main_frame, text="Configuración", padding=10)
        # Empaqueta en la parte SUPERIOR, rellenando solo X
        config_frame.pack(fill=X, pady=5, side=TOP) 

        # Directorio de Salida
        ttk.Label(config_frame, text="Directorio de Salida:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.output_dir_var = ttk.StringVar(value="output")
        output_entry = ttk.Entry(config_frame, textvariable=self.output_dir_var, width=50)
        output_entry.grid(row=0, column=1, padx=5, pady=5, sticky=EW)
        
        # Botón morado (usa el estilo PRIMARY)
        browse_btn = ttk.Button(config_frame, text="Examinar...", command=self.browse_output_dir, style=PRIMARY)
        browse_btn.grid(row=0, column=2, padx=5, pady=5)

        # Tamaño Final
        ttk.Label(config_frame, text="Tamaño Final (Ancho x Alto):").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        
        self.width_var = ttk.IntVar(value=250)
        self.height_var = ttk.IntVar(value=400)
        
        size_frame = ttk.Frame(config_frame)
        size_frame.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        
        ttk.Entry(size_frame, textvariable=self.width_var, width=8).pack(side=LEFT, padx=2)
        ttk.Label(size_frame, text="x").pack(side=LEFT, padx=5)
        ttk.Entry(size_frame, textvariable=self.height_var, width=8).pack(side=LEFT, padx=2)
        
        # --- Selector de Temas ---
        ttk.Label(config_frame, text="Tema:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        
        self.theme_combobox = ttk.Combobox(
            config_frame, 
            values=list(self.theme_map.keys()), # Usa los nombres bonitos
            state="readonly"
        )
        self.theme_combobox.set("Dark") # El tema inicial
        
        self.theme_combobox.grid(row=2, column=1, padx=5, pady=5, sticky=W)
        
        # "Bind" (conectar) el combobox a una función
        self.theme_combobox.bind("<<ComboboxSelected>>", self.change_theme)
        
        config_frame.columnconfigure(1, weight=1)

        # --- SECCIÓN DE LISTA DE IMÁGENES ---
        list_frame = ttk.Labelframe(main_frame, text="Imágenes a Procesar", padding=10)
        # Empaqueta en la parte SUPERIOR, rellenando solo X. NO se expande.
        list_frame.pack(fill=X, pady=10, side=TOP) 
        
        # Entradas para añadir imagen
        add_frame = ttk.Frame(list_frame)
        add_frame.pack(fill=X, pady=5)
        ttk.Label(add_frame, text="Nombre:").pack(side=LEFT, padx=5)
        self.entry_name = ttk.Entry(add_frame, width=20)
        self.entry_name.pack(side=LEFT, padx=5)
        ttk.Label(add_frame, text="URL:").pack(side=LEFT, padx=5)
        self.entry_url = ttk.Entry(add_frame, width=40)
        self.entry_url.pack(side=LEFT, padx=5, fill=X, expand=YES)
        add_btn = ttk.Button(add_frame, text="Añadir", command=self.add_image_to_list, style=SUCCESS)
        add_btn.pack(side=LEFT, padx=5)

        # El Treeview (lista)
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=BOTH, expand=YES, pady=5)
        
        cols = ("Nombre", "URL")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=8)
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("URL", text="URL")
        self.tree.column("Nombre", width=200, stretch=NO)
        self.tree.column("URL", stretch=YES)
        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        
        # Scrollbar para el Treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Botón de eliminar
        remove_btn = ttk.Button(list_frame, text="Eliminar Seleccionado", command=self.remove_selected_image, style=DANGER)
        remove_btn.pack(anchor=E, pady=5, padx=5)

        # --- CAMBIO DE LAYOUT ---
        # Empaquetamos los elementos de abajo en orden inverso
        # para que el botón "Iniciar Proceso" esté siempre en el fondo.
        
        # --- ¡AQUÍ ESTÁ TU BOTÓN DE DESCARGA! ---
        # 1. Empaqueta el botón de INICIO en la parte INFERIOR
        self.start_button = ttk.Button(main_frame, text="Iniciar Proceso", command=self.start_processing, style=PRIMARY)
        self.start_button.pack(side=BOTTOM, fill=X, pady=10, ipady=5)

        # --- SECCIÓN DE PROGRESO Y LOG ---
        # 2. Empaqueta el LOG en la parte INFERIOR (quedará *encima* del botón)
        #    Se expandirá para rellenar el espacio sobrante.
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=BOTH, expand=YES, side=BOTTOM, pady=5)

        self.log_text = ttk.Text(log_frame, height=5, state=DISABLED, width=80)
        log_scroll = ttk.Scrollbar(log_frame, orient=VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side=LEFT, fill=BOTH, expand=YES)
        log_scroll.pack(side=RIGHT, fill=Y)
                        
    # --- MÉTODOS CALLBACK (Acciones de botones) ---

    def change_theme(self, event=None):
        """Cambia el tema de la aplicación y reaplica los estilos."""
        display_name = self.theme_combobox.get()
        internal_name = self.theme_map.get(display_name)
        if not internal_name:
            print(f"Error: Tema '{display_name}' no encontrado en el mapa.")
            return
        self.style.theme_use(internal_name)
        self.apply_custom_styles()


    def browse_output_dir(self):
        """Abre un diálogo para seleccionar una carpeta."""
        dir_name = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if dir_name:
            self.output_dir_var.set(dir_name)

    def add_image_to_list(self):
        """Añade los datos de los Entry al Treeview."""
        name = self.entry_name.get()
        url = self.entry_url.get()
        
        if not name or not url:
            self.log_message("ERROR: Debes rellenar Nombre y URL.", "danger")
            return
            
        self.tree.insert("", END, values=(name, url))
        
        # Limpiar campos
        self.entry_name.delete(0, END)
        self.entry_url.delete(0, END)
        self.entry_name.focus()

    def remove_selected_image(self):
        """Elimina la(s) fila(s) seleccionada(s) del Treeview."""
        selected_items = self.tree.selection()
        if not selected_items:
            self.log_message("AVISO: No hay ninguna imagen seleccionada para eliminar.", "warning")
            return
        
        for item in selected_items:
            self.tree.delete(item)

    # --- FUNCIÓN log_message CORREGIDA ---
    def log_message(self, message, style="default"):
        """Añade un mensaje al Text de log de forma segura."""
        self.log_text.config(state=NORMAL)
        
        if style != "default":
            # Forma segura de obtener el color del tema
            color = getattr(self.style.colors, style, None)
            
            if color:
                if not style in self.log_text.tag_config(style):
                    self.log_text.tag_configure(style, foreground=color)
                self.log_text.insert(END, message + "\n", style)
            else:
                self.log_text.insert(END, message + "\n")
        else:
            self.log_text.insert(END, message + "\n")
            
        self.log_text.config(state=DISABLED)
        self.log_text.see(END)

    def poll_log_queue(self):
        """Revisa la cola de logs cada 100ms."""
        try:
            while True:
                record = self.log_queue.get(block=False)
                msg, style = record
                
                if msg == "!!PROCESSING_DONE!!":
                    self.is_processing = False
                    self.start_button.config(text="Iniciar Proceso", state=NORMAL)
                    self.log_message("\n🎉 ¡Proceso completado!", "success")
                else:
                    self.log_message(msg, style)
                    
        except queue.Empty:
            pass
        
        self.after(100, self.poll_log_queue)

    def start_processing(self):
        """Inicia el proceso de descarga en un hilo separado."""
        if self.is_processing:
            return

        images_to_process = []
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, "values")
            images_to_process.append({"name": values[0], "url": values[1]})
            
        if not images_to_process:
            self.log_message("AVISO: No hay imágenes en la lista para procesar.", "warning")
            return

        try:
            output_dir = self.output_dir_var.get()
            final_size = (self.width_var.get(), self.height_var.get())
            if final_size[0] <= 0 or final_size[1] <= 0:
                raise ValueError("El tamaño debe ser positivo")
        except Exception:
            self.log_message("ERROR: Tamaño (Ancho/Alto) no válido. Deben ser números.", "danger")
            return

        self.is_processing = True
        self.start_button.config(text="Procesando...", state=DISABLED)
        self.log_text.config(state=NORMAL)
        self.log_text.delete(1.0, END)
        self.log_text.config(state=DISABLED)
        self.log_message(f"Iniciando proceso para {len(images_to_process)} imágenes...", "info")

        thread = threading.Thread(
            target=self.processing_worker, 
            args=(images_to_process, output_dir, final_size),
            daemon=True
        )
        thread.start()

    def processing_worker(self, images_list, output_dir, final_size):
        """Esta función se ejecuta en el HILO SECUNDARIO."""
        total = len(images_list)
        ok = 0
        
        for i, img_data in enumerate(images_list):
            name = img_data["name"]
            url = img_data["url"]
            
            self.log_queue.put((f"({i+1}/{total}) Procesando: {name}...", "default"))
            
            status_msg = process_image_entry(name, url, output_dir, final_size)
            
            if status_msg.startswith("✅"):
                ok += 1
                self.log_queue.put((status_msg, "success"))
            else:
                self.log_queue.put((status_msg, "danger"))
        
        self.log_queue.put((f"\nResumen: {ok}/{total} completadas.", "info"))
        
        # Enviar el mensaje especial de "listo"
        self.log_queue.put(("!!PROCESSING_DONE!!", "default"))


# --- 4. PUNTO DE ENTRADA (Al final de todo) ---
if __name__ == "__main__":
    app = ResizerApp()
    app.mainloop()