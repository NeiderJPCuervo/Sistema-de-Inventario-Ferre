"""
╔══════════════════════════════════════════════════════════════════╗
║         FERRETERÍA — SISTEMA DE GESTIÓN                          ║
║         Todo se adapta al tamaño de fuente y pantalla            ║
╚══════════════════════════════════════════════════════════════════╝
EJECUTAR:  python ferreteria_gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ════════════════════════════════════════════════════════════════
#  ESCALA ADAPTABLE
#  Se calcula UNA VEZ al iniciar y todos los tamaños la usan.
#  Si la pantalla es grande o la fuente del sistema es grande,
#  todo el programa crece proporcionalmente.
# ════════════════════════════════════════════════════════════════

_root_tmp = tk.Tk()
_root_tmp.withdraw()

# DPI de la pantalla (puntos por pulgada)
# En pantallas normales ~96 dpi, en 4K/HiDPI puede ser 144-192
_DPI = _root_tmp.winfo_fpixels("1i")

# Factor de escala: 1.0 = pantalla normal (96 dpi)
# En pantallas HiDPI el factor sube y todo crece con él
ESCALA = max(1.0, _DPI / 96.0)

_root_tmp.destroy()


def e(n):
    """Escala un número de píxeles según el DPI de la pantalla."""
    return max(1, int(n * ESCALA))


def fs(n):
    """Devuelve un tamaño de fuente escalado."""
    return max(8, int(n * ESCALA))


# ════════════════════════════════════════════════════════════════
#  PALETA DE COLORES
# ════════════════════════════════════════════════════════════════
C = {
    "fondo":           "#F4F4F4",
    "sidebar_bg":      "#2B2B2B",
    "sidebar_hover":   "#3D3D3D",
    "naranja":         "#E8720C",
    "naranja_oscuro":  "#C45E08",
    "header_bg":       "#2B2B2B",
    "texto":           "#1A1A1A",
    "texto_claro":     "#FFFFFF",
    "texto_gris":      "#6B6B6B",
    "tabla_header":    "#E8720C",
    "tabla_fila1":     "#FFFFFF",
    "tabla_fila2":     "#FFF3E8",
    "tabla_seleccion": "#FFD4A8",
    "btn_primario":    "#E8720C",
    "btn_secundario":  "#555555",
    "btn_peligro":     "#C0392B",
    "btn_exito":       "#27AE60",
    "borde":           "#DDDDDD",
}

# ════════════════════════════════════════════════════════════════
#  BASE DE DATOS
# ════════════════════════════════════════════════════════════════
DB = "ferreteria.db"


def db_connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()


def db_init():
    conn, cur = db_connect()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS categorias (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL UNIQUE,
            descripcion TEXT
        );
        CREATE TABLE IF NOT EXISTS productos (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo        TEXT UNIQUE NOT NULL,
            nombre        TEXT NOT NULL,
            descripcion   TEXT,
            precio_compra REAL NOT NULL DEFAULT 0,
            precio_venta  REAL NOT NULL DEFAULT 0,
            stock         INTEGER NOT NULL DEFAULT 0,
            stock_minimo  INTEGER NOT NULL DEFAULT 5,
            categoria_id  INTEGER,
            fecha_registro TEXT,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        );

        CREATE TABLE IF NOT EXISTS ventas (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            numero  TEXT NOT NULL UNIQUE,
            cliente TEXT NOT NULL DEFAULT 'Público General',
            fecha   TEXT NOT NULL,
            total   REAL NOT NULL DEFAULT 0,
            estado  TEXT NOT NULL DEFAULT 'completada'
        );

        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id    INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            codigo      TEXT NOT NULL,
            nombre      TEXT NOT NULL,
            cantidad    INTEGER NOT NULL,
            precio_unit REAL NOT NULL,
            subtotal    REAL NOT NULL,
            FOREIGN KEY (venta_id)    REFERENCES ventas(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        );
    """)
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════════
#  COMPONENTES VISUALES REUTILIZABLES
# ════════════════════════════════════════════════════════════════

def make_button(parent, text, command, color=None, pad=None):
    """
    Botón con tamaño y fuente que se adaptan a la escala de pantalla.
    No tiene ancho fijo: se ajusta al texto automáticamente.
    """
    bg  = color or C["btn_primario"]
    pad = pad if pad is not None else e(7)

    def on_enter(e_): btn.config(bg=C["naranja_oscuro"] if bg == C["btn_primario"] else "#444")
    def on_leave(e_): btn.config(bg=bg)

    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=C["texto_claro"],
        font=("Segoe UI", fs(10), "bold"),
        relief="flat",
        cursor="hand2",
        padx=e(14),
        pady=pad,
        bd=0,
        activebackground=C["naranja_oscuro"],
        activeforeground=C["texto_claro"],
    )
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def make_treeview(parent, columns):
    """
    Tabla adaptable:
    • Sin altura fija — crece con el frame contenedor.
    • Columnas con stretch=True — se reparten el espacio disponible.
    • Scrollbar vertical y horizontal siempre disponibles.
    • Fuente y altura de fila escaladas según DPI.
    """
    style = ttk.Style()
    style.theme_use("default")
    style.configure("F.Treeview.Heading",
                    background=C["tabla_header"],
                    foreground=C["texto_claro"],
                    font=("Segoe UI", fs(10), "bold"),
                    relief="flat")
    style.configure("F.Treeview",
                    background=C["tabla_fila1"],
                    foreground=C["texto"],
                    font=("Segoe UI", fs(10)),
                    rowheight=e(30),
                    fieldbackground=C["tabla_fila1"])
    style.map("F.Treeview",
              background=[("selected", C["tabla_seleccion"])],
              foreground=[("selected", C["texto"])])

    frame = tk.Frame(parent, bg=C["fondo"])
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    tree = ttk.Treeview(frame,
                        columns=[c[0] for c in columns],
                        show="headings",
                        style="F.Treeview")

    vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    for col_id, peso, anchor in columns:
        tree.heading(col_id, text=col_id)
        tree.column(col_id,
                    minwidth=e(max(50, peso * 7)),
                    width=e(max(70, peso * 9)),
                    anchor=anchor,
                    stretch=True)

    tree.tag_configure("par",    background=C["tabla_fila1"])
    tree.tag_configure("impar",  background=C["tabla_fila2"])
    tree.tag_configure("alerta", background="#FFE0E0", foreground="#C0392B")

    return frame, tree


def limpiar_tree(tree):
    for item in tree.get_children():
        tree.delete(item)


def insertar_fila(tree, valores, tag=None):
    if tag == "alerta":
        tree.insert("", "end", values=valores, tags=("alerta",))
    else:
        n = len(tree.get_children())
        tree.insert("", "end", values=valores,
                    tags=("par" if n % 2 == 0 else "impar",))


def hacer_header(parent, texto):
    """Encabezado oscuro con fuente escalada."""
    hdr = tk.Frame(parent, bg=C["header_bg"])
    hdr.grid(row=0, column=0, sticky="ew")
    tk.Label(hdr, text=texto,
             font=("Segoe UI", fs(15), "bold"),
             bg=C["header_bg"], fg="white",
             pady=e(13)).pack(side="left", padx=e(18))


def hacer_notebook(parent):
    """Pestañas con estilo naranja y fuente escalada."""
    s = ttk.Style()
    s.configure("TNotebook", background=C["fondo"])
    s.configure("TNotebook.Tab",
                font=("Segoe UI", fs(10), "bold"),
                padding=[e(12), e(6)])
    s.map("TNotebook.Tab",
          background=[("selected", C["naranja"])],
          foreground=[("selected", "white")])
    nb = ttk.Notebook(parent)
    nb.grid(row=2, column=0, sticky="nsew",
            padx=e(12), pady=(0, e(12)))
    return nb


# ════════════════════════════════════════════════════════════════
#  VENTANA MODAL BASE
#  Auto-dimensionada según el contenido real que tenga.
# ════════════════════════════════════════════════════════════════

class DialogBase(tk.Toplevel):
    """
    Ventana modal que:
    • Mide su propio contenido y se ajusta automáticamente.
    • Es redimensionable libremente.
    • Tiene scroll si el contenido no cabe.
    • Fuentes y espaciados escalados al DPI.
    """

    def __init__(self, parent, titulo):
        super().__init__(parent)
        self.title(titulo)
        self.configure(bg=C["fondo"])
        self.resizable(True, True)
        self.minsize(e(380), e(250))
        self.transient(parent)
        self.grab_set()

        # Encabezado naranja
        hdr = tk.Frame(self, bg=C["naranja"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=titulo,
                 font=("Segoe UI", fs(13), "bold"),
                 bg=C["naranja"], fg="white",
                 pady=e(12)).pack(padx=e(18), anchor="w")

        # Zona de scroll para los campos
        wrap = tk.Frame(self, bg=C["fondo"])
        wrap.pack(fill="both", expand=True)
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(wrap, bg=C["fondo"],
                                  highlightthickness=0)
        self._vsb = ttk.Scrollbar(wrap, orient="vertical",
                                   command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vsb.set)

        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._vsb.grid(row=0, column=1, sticky="ns")

        self.body = tk.Frame(self._canvas, bg=C["fondo"],
                              padx=e(24), pady=e(16))
        self.body.columnconfigure(1, weight=1)

        self._win = self._canvas.create_window(
            (0, 0), window=self.body, anchor="nw")

        self.body.bind("<Configure>", self._on_body_cfg)
        self._canvas.bind("<Configure>", self._on_canvas_cfg)
        self._canvas.bind_all("<MouseWheel>", self._on_scroll)

        # Barra de botones fija en la parte inferior
        self._bar = tk.Frame(self, bg=C["fondo"], pady=e(10))
        self._bar.pack(fill="x", side="bottom")
        tk.Frame(self._bar, bg=C["borde"], height=1).pack(
            fill="x", padx=e(16), pady=(0, e(10)))

    def _on_body_cfg(self, _):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_cfg(self, event):
        self._canvas.itemconfig(self._win, width=event.width)

    def _on_scroll(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def campo(self, label, fila, valor=""):
        """Agrega un campo de texto al formulario. Retorna el Entry."""
        tk.Label(self.body, text=label,
                 font=("Segoe UI", fs(10), "bold"),
                 bg=C["fondo"], fg=C["texto"],
                 anchor="w").grid(
            row=fila, column=0, sticky="w",
            pady=e(7), padx=(0, e(12)))

        e_ = tk.Entry(self.body,
                      font=("Segoe UI", fs(11)),
                      relief="flat", bg="white",
                      fg=C["texto"],
                      highlightthickness=1,
                      highlightbackground=C["borde"],
                      highlightcolor=C["naranja"])
        e_.grid(row=fila, column=1, sticky="ew", pady=e(7))

        if valor != "":
            e_.insert(0, str(valor))
        return e_

    def combo(self, label, fila, opciones, default=0):
        """Agrega un desplegable al formulario. Retorna el Combobox."""
        tk.Label(self.body, text=label,
                 font=("Segoe UI", fs(10), "bold"),
                 bg=C["fondo"], fg=C["texto"],
                 anchor="w").grid(
            row=fila, column=0, sticky="w",
            pady=e(7), padx=(0, e(12)))

        cb = ttk.Combobox(self.body, values=opciones,
                          state="readonly",
                          font=("Segoe UI", fs(11)))
        cb.grid(row=fila, column=1, sticky="ew", pady=e(7))
        if opciones:
            cb.current(default)
        return cb

    def botones(self, ok_text="Guardar", ok_cmd=None, cancel_cmd=None):
        """Coloca botones y luego ajusta el tamaño de la ventana al contenido."""
        make_button(self._bar, f"✔  {ok_text}",
                    ok_cmd or self.destroy).pack(side="right", padx=e(4))
        make_button(self._bar, "✖  Cancelar",
                    cancel_cmd or self.destroy,
                    color=C["btn_secundario"]).pack(side="right", padx=e(4))

        # Ajustar tamaño automáticamente al contenido real
        self.after(10, self._autosize)

    def _autosize(self):
        """Calcula el tamaño ideal basado en el contenido y centra la ventana."""
        self.update_idletasks()
        w = self.body.winfo_reqwidth()  + e(70)
        h = self.body.winfo_reqheight() + e(130)

        # Limitar al 85% de la pantalla
        max_w = int(self.winfo_screenwidth()  * 0.85)
        max_h = int(self.winfo_screenheight() * 0.85)
        w = min(w, max_w)
        h = min(h, max_h)

        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")


# ════════════════════════════════════════════════════════════════
#  MÓDULO 1A — CATEGORÍAS
# ════════════════════════════════════════════════════════════════

class PanelCategorias(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C["fondo"])
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        hacer_header(self, "⚙  CATEGORÍAS")

        tools = tk.Frame(self, bg=C["fondo"],
                         pady=e(10), padx=e(14))
        tools.grid(row=1, column=0, sticky="ew")
        make_button(tools, "＋  Nueva Categoría",
                    self.nueva_categoria).pack(side="left")

        cols = [
            ("ID",           5,  "center"),
            ("Nombre",       20, "w"),
            ("Descripción",  40, "w"),
        ]
        tf, self.tree = make_treeview(self, cols)
        tf.grid(row=2, column=0, sticky="nsew",
                padx=e(14), pady=(0, e(14)))
        self.cargar()

    def cargar(self):
        limpiar_tree(self.tree)
        conn, cur = db_connect()
        cur.execute(
            "SELECT id, nombre, COALESCE(descripcion,'') "
            "FROM categorias ORDER BY nombre")
        for r in cur.fetchall():
            insertar_fila(self.tree, tuple(r))
        conn.close()

    def nueva_categoria(self):
        dlg   = DialogBase(self.winfo_toplevel(), "Nueva Categoría")
        e_nom  = dlg.campo("Nombre de la categoría:", 0)
        e_desc = dlg.campo("Descripción (opcional):",  1)

        def guardar():
            nom  = e_nom.get().strip()
            desc = e_desc.get().strip()
            if not nom:
                messagebox.showerror("Error",
                    "El nombre no puede estar vacío.", parent=dlg)
                return
            try:
                conn, cur = db_connect()
                cur.execute(
                    "INSERT INTO categorias (nombre, descripcion) VALUES (?,?)",
                    (nom, desc))
                conn.commit(); conn.close()
                messagebox.showinfo("✔ Listo",
                    f"Categoría '{nom}' creada.", parent=dlg)
                dlg.destroy(); self.cargar()
            except sqlite3.IntegrityError:
                messagebox.showerror("Duplicado",
                    f"La categoría '{nom}' ya existe.", parent=dlg)

        dlg.botones("Guardar", guardar)


# ════════════════════════════════════════════════════════════════
#  MÓDULO 1B — PRODUCTOS
# ════════════════════════════════════════════════════════════════

class PanelProductos(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C["fondo"])
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        hacer_header(self, "📦  PRODUCTOS")

        tools = tk.Frame(self, bg=C["fondo"],
                         pady=e(10), padx=e(14))
        tools.grid(row=1, column=0, sticky="ew")
        tools.columnconfigure(3, weight=1)

        make_button(tools, "＋  Nuevo",
                    self.nuevo_producto).grid(row=0, column=0, padx=(0, e(6)))
        make_button(tools, "✏  Editar Precio",
                    self.editar_precio,
                    color=C["btn_secundario"]).grid(row=0, column=1, padx=(0, e(6)))
        make_button(tools, "📥 Agregar Stock",
                    self.agregar_stock,
                    color=C["btn_exito"]).grid(row=0, column=2)

        # Buscador alineado a la derecha
        bf = tk.Frame(tools, bg=C["fondo"])
        bf.grid(row=0, column=4, sticky="e")
        tk.Label(bf, text="🔍  Buscar:",
                 font=("Segoe UI", fs(10)),
                 bg=C["fondo"]).pack(side="left", padx=(0, e(4)))

        self.var_buscar = tk.StringVar()
        self.var_buscar.trace_add("write", lambda *_: self.cargar())
        tk.Entry(bf,
                 textvariable=self.var_buscar,
                 font=("Segoe UI", fs(11)),
                 width=22, relief="flat",
                 highlightthickness=1,
                 highlightbackground=C["borde"],
                 highlightcolor=C["naranja"]).pack(side="left")

        cols = [
            ("Código",     8,  "center"),
            ("Nombre",     22, "w"),
            ("Categoría",  12, "center"),
            ("P. Compra",  10, "center"),
            ("P. Venta",   10, "center"),
            ("Stock",       7, "center"),
            ("Mín.",        6, "center"),
            ("Estado",      8, "center"),
        ]
        tf, self.tree = make_treeview(self, cols)
        tf.grid(row=2, column=0, sticky="nsew",
                padx=e(14), pady=(0, e(14)))
        self.cargar()

    def cargar(self):
        limpiar_tree(self.tree)
        t = self.var_buscar.get().strip()
        conn, cur = db_connect()
        cur.execute("""
            SELECT p.codigo, p.nombre, COALESCE(c.nombre,'Sin cat.'),
                   p.precio_compra, p.precio_venta, p.stock, p.stock_minimo
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.nombre LIKE ? OR p.codigo LIKE ?
            ORDER BY p.nombre
        """, (f"%{t}%", f"%{t}%"))
        for r in cur.fetchall():
            bajo   = r[5] <= r[6]
            estado = "⚠ BAJO" if bajo else "✔ OK"
            insertar_fila(self.tree,
                (r[0], r[1], r[2],
                 f"Q {r[3]:,.2f}", f"Q {r[4]:,.2f}",
                 r[5], r[6], estado),
                tag="alerta" if bajo else None)
        conn.close()

    def nuevo_producto(self):
        conn, cur = db_connect()
        cur.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
        cats = cur.fetchall(); conn.close()

        if not cats:
            messagebox.showwarning("Sin categorías",
                "Primero crea al menos una categoría\n"
                "en el módulo ⚙ Categorías.")
            return

        dlg    = DialogBase(self.winfo_toplevel(), "Registrar Nuevo Producto")
        e_cod  = dlg.campo("Código  (ej: MART-001):",  0)
        e_nom  = dlg.campo("Nombre del producto:",      1)
        e_desc = dlg.campo("Descripción (opcional):",   2)
        e_pc   = dlg.campo("Precio de compra (Q):",     3)
        e_pv   = dlg.campo("Precio de venta  (Q):",     4)
        e_stk  = dlg.campo("Stock inicial:",             5)
        e_min  = dlg.campo("Stock mínimo para alerta:", 6, "5")
        cb_cat = dlg.combo("Categoría:",                 7, [c[1] for c in cats])

        def guardar():
            try:
                cod    = e_cod.get().strip().upper()
                nom    = e_nom.get().strip()
                desc   = e_desc.get().strip()
                pc     = float(e_pc.get())
                pv     = float(e_pv.get())
                stk    = int(e_stk.get())
                mn     = int(e_min.get())
                cat_id = cats[cb_cat.current()][0]
                if not cod or not nom:
                    messagebox.showerror("Error",
                        "Código y nombre son obligatorios.", parent=dlg)
                    return
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn, cur = db_connect()
                cur.execute("""
                    INSERT INTO productos
                    (codigo,nombre,descripcion,precio_compra,precio_venta,
                     stock,stock_minimo,categoria_id,fecha_registro)
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, (cod,nom,desc,pc,pv,stk,mn,cat_id,fecha))
                conn.commit(); conn.close()
                messagebox.showinfo("✔ Listo",
                    f"Producto '{nom}' registrado.", parent=dlg)
                dlg.destroy(); self.cargar()
            except ValueError:
                messagebox.showerror("Error",
                    "Precios y stock deben ser números.", parent=dlg)
            except sqlite3.IntegrityError:
                messagebox.showerror("Código duplicado",
                    "Ese código ya existe.", parent=dlg)

        dlg.botones("Guardar", guardar)

    def editar_precio(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona",
                "Haz clic en un producto de la tabla primero.")
            return
        codigo = self.tree.item(sel[0])["values"][0]
        conn, cur = db_connect()
        cur.execute(
            "SELECT nombre, precio_compra, precio_venta "
            "FROM productos WHERE codigo=?", (codigo,))
        prod = cur.fetchone(); conn.close()

        dlg  = DialogBase(self.winfo_toplevel(),
                          f"Editar Precios — {prod[0]}")
        e_pc = dlg.campo("Nuevo precio de compra (Q):", 0, prod[1])
        e_pv = dlg.campo("Nuevo precio de venta  (Q):", 1, prod[2])

        def guardar():
            try:
                pc = float(e_pc.get()); pv = float(e_pv.get())
                conn, cur = db_connect()
                cur.execute(
                    "UPDATE productos SET precio_compra=?, precio_venta=? "
                    "WHERE codigo=?", (pc, pv, codigo))
                conn.commit(); conn.close()
                messagebox.showinfo("✔ Listo",
                    "Precios actualizados.", parent=dlg)
                dlg.destroy(); self.cargar()
            except ValueError:
                messagebox.showerror("Error",
                    "Ingresa números válidos.", parent=dlg)

        dlg.botones("Actualizar", guardar)

    def agregar_stock(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona",
                "Haz clic en un producto de la tabla primero.")
            return
        vals         = self.tree.item(sel[0])["values"]
        codigo, nombre, stock_actual = vals[0], vals[1], vals[5]

        dlg   = DialogBase(self.winfo_toplevel(),
                           f"Agregar Stock — {nombre}")
        tk.Label(dlg.body,
                 text=f"Stock actual:  {stock_actual} unidades",
                 font=("Segoe UI", fs(11), "bold"),
                 bg=C["fondo"], fg=C["naranja"]).grid(
            row=0, column=0, columnspan=2,
            sticky="w", pady=(0, e(12)))
        e_qty = dlg.campo("Cantidad a ingresar:", 1)

        def guardar():
            try:
                qty = int(e_qty.get())
                if qty <= 0: raise ValueError
                conn, cur = db_connect()
                cur.execute(
                    "UPDATE productos SET stock = stock + ? WHERE codigo=?",
                    (qty, codigo))
                conn.commit(); conn.close()
                messagebox.showinfo("✔ Listo",
                    f"Nuevo total: {stock_actual + qty} unidades.",
                    parent=dlg)
                dlg.destroy(); self.cargar()
            except ValueError:
                messagebox.showerror("Error",
                    "Ingresa un número entero mayor a 0.", parent=dlg)

        dlg.botones("Ingresar Stock", guardar)


# ════════════════════════════════════════════════════════════════
#  MÓDULO 3 — INVENTARIO
# ════════════════════════════════════════════════════════════════

class PanelInventario(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C["fondo"])
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        hacer_header(self, "🗂  INVENTARIO")

        tools = tk.Frame(self, bg=C["fondo"],
                         pady=e(10), padx=e(14))
        tools.grid(row=1, column=0, sticky="ew")
        make_button(tools, "🔄  Actualizar",
                    self.cargar, pad=e(6)).pack(side="left")

        nb = hacer_notebook(self)

        # Tab 1 — Inventario completo
        tab1 = tk.Frame(nb, bg=C["fondo"])
        tab1.rowconfigure(0, weight=1)
        tab1.columnconfigure(0, weight=1)
        nb.add(tab1, text="  📋 Inventario Completo  ")

        tf1, self.tree_inv = make_treeview(tab1, [
            ("Categoría",  13, "center"),
            ("Código",      9, "center"),
            ("Producto",   20, "w"),
            ("Stock",       7, "center"),
            ("Mín.",        6, "center"),
            ("P. Venta",    9, "center"),
            ("Estado",      9, "center"),
        ])
        tf1.grid(row=0, column=0, sticky="nsew",
                 padx=e(8), pady=e(8))

        # Tab 2 — Alertas
        tab2 = tk.Frame(nb, bg=C["fondo"])
        tab2.rowconfigure(1, weight=1)
        tab2.columnconfigure(0, weight=1)
        nb.add(tab2, text="  ⚠  Alertas de Stock  ")

        self.lbl_nalerts = tk.Label(
            tab2, text="",
            font=("Segoe UI", fs(11), "bold"),
            bg=C["fondo"], fg=C["btn_peligro"],
            anchor="w", wraplength=900)
        self.lbl_nalerts.grid(row=0, column=0,
                               sticky="ew", padx=e(10), pady=(e(8), e(2)))

        tf2, self.tree_alert = make_treeview(tab2, [
            ("Código",    9,  "center"),
            ("Producto",  22, "w"),
            ("Categoría", 13, "center"),
            ("Stock",      8, "center"),
            ("Mínimo",     8, "center"),
            ("Estado",    10, "center"),
        ])
        tf2.grid(row=1, column=0, sticky="nsew",
                 padx=e(8), pady=(0, e(8)))

        # Tab 3 — Valor
        tab3 = tk.Frame(nb, bg=C["fondo"])
        tab3.rowconfigure(0, weight=1)
        tab3.columnconfigure(0, weight=1)
        nb.add(tab3, text="  💰 Valor del Inventario  ")

        tf3, self.tree_val = make_treeview(tab3, [
            ("Categoría",          18, "w"),
            ("Valor Costo",        14, "center"),
            ("Valor Venta",        14, "center"),
            ("Ganancia Potencial", 16, "center"),
        ])
        tf3.grid(row=0, column=0, sticky="nsew",
                 padx=e(8), pady=(e(8), 0))

        self.lbl_totales = tk.Label(
            tab3, text="",
            font=("Segoe UI", fs(11), "bold"),
            bg=C["fondo"], fg=C["naranja"],
            anchor="center", wraplength=900)
        self.lbl_totales.grid(row=1, column=0,
                               sticky="ew", padx=e(10), pady=e(8))

        self.cargar()

    def cargar(self):
        conn, cur = db_connect()

        limpiar_tree(self.tree_inv)
        cur.execute("""
            SELECT COALESCE(c.nombre,'Sin cat.'), p.codigo, p.nombre,
                   p.stock, p.stock_minimo, p.precio_venta
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            ORDER BY c.nombre, p.nombre
        """)
        for r in cur.fetchall():
            bajo = r[3] <= r[4]
            insertar_fila(self.tree_inv,
                (r[0], r[1], r[2], r[3], r[4],
                 f"Q {r[5]:,.2f}",
                 "⚠ REABASTECER" if bajo else "✔ OK"),
                tag="alerta" if bajo else None)

        limpiar_tree(self.tree_alert)
        cur.execute("""
            SELECT p.codigo, p.nombre, COALESCE(c.nombre,'—'),
                   p.stock, p.stock_minimo
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.stock <= p.stock_minimo
            ORDER BY p.stock ASC
        """)
        alertas = cur.fetchall()
        self.lbl_nalerts.config(
            text=(f"  ⚠  {len(alertas)} producto(s) requieren reposición"
                  if alertas
                  else "  ✔  Todo el inventario está en niveles adecuados"))
        for r in alertas:
            insertar_fila(self.tree_alert,
                (r[0], r[1], r[2], r[3], r[4],
                 "🔴 AGOTADO" if r[3] == 0 else "🟡 BAJO"),
                tag="alerta")

        limpiar_tree(self.tree_val)
        cur.execute("""
            SELECT COALESCE(c.nombre,'Sin cat.'),
                   COALESCE(SUM(p.stock*p.precio_compra),0),
                   COALESCE(SUM(p.stock*p.precio_venta),0)
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            GROUP BY c.nombre ORDER BY c.nombre
        """)
        tc = tv = 0.0
        for r in cur.fetchall():
            co = r[1]; ve = r[2]
            tc += co; tv += ve
            insertar_fila(self.tree_val,
                (r[0], f"Q {co:,.2f}",
                 f"Q {ve:,.2f}", f"Q {ve-co:,.2f}"))
        self.lbl_totales.config(
            text=(f"Total invertido: Q {tc:,.2f}     │     "
                  f"Valor de venta: Q {tv:,.2f}     │     "
                  f"Ganancia potencial: Q {tv-tc:,.2f}"))
        conn.close()


# ════════════════════════════════════════════════════════════════
#  MÓDULO 5 — REPORTES
# ════════════════════════════════════════════════════════════════

class PanelReportes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C["fondo"])
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        hacer_header(self, "📊  REPORTES")

        nb = hacer_notebook(self)

        # ── Tab 1: KPI ───────────────────────────────────────────
        self.tab_res = tk.Frame(nb, bg=C["fondo"])
        self.tab_res.rowconfigure(2, weight=1)
        self.tab_res.columnconfigure(0, weight=1)
        nb.add(self.tab_res, text="  📋 Resumen General  ")

        tk.Label(self.tab_res,
                 text="Indicadores generales del negocio",
                 font=("Segoe UI", fs(11)),
                 bg=C["fondo"], fg=C["texto_gris"]).grid(
            row=0, column=0, pady=(e(12), e(4)))
        make_button(self.tab_res, "🔄  Actualizar",
                    self._cargar_resumen,
                    pad=e(6)).grid(row=1, column=0, pady=(0, e(4)))

        self.frame_kpi = tk.Frame(self.tab_res, bg=C["fondo"])
        self.frame_kpi.grid(row=2, column=0, sticky="nsew",
                             padx=e(20), pady=e(10))
        self._cargar_resumen()

        # ── Tab 2: Por categoría ─────────────────────────────────
        tab2 = tk.Frame(nb, bg=C["fondo"])
        tab2.rowconfigure(1, weight=1)
        tab2.columnconfigure(0, weight=1)
        nb.add(tab2, text="  📦 Productos por Categoría  ")

        make_button(tab2, "🔄  Actualizar",
                    lambda: self._cargar_por_cat(),
                    pad=e(6)).grid(
            row=0, column=0, sticky="w",
            padx=e(10), pady=(e(10), e(4)))
        tf2, self.tree_cat = make_treeview(tab2, [
            ("Categoría",            22, "w"),
            ("Nº Productos",         12, "center"),
            ("Stock Total",          12, "center"),
            ("Precio Venta Prom.",   16, "center"),
        ])
        tf2.grid(row=1, column=0, sticky="nsew",
                 padx=e(8), pady=(0, e(8)))
        self._cargar_por_cat()

        # ── Tab 3: Valor por categoría ───────────────────────────
        tab3 = tk.Frame(nb, bg=C["fondo"])
        tab3.rowconfigure(1, weight=1)
        tab3.columnconfigure(0, weight=1)
        nb.add(tab3, text="  💰 Valor por Categoría  ")

        make_button(tab3, "🔄  Actualizar",
                    lambda: self._cargar_valor_cat(),
                    pad=e(6)).grid(
            row=0, column=0, sticky="w",
            padx=e(10), pady=(e(10), e(4)))
        tf3, self.tree_val_cat = make_treeview(tab3, [
            ("Categoría",          18, "w"),
            ("Valor Costo",        14, "center"),
            ("Valor Venta",        14, "center"),
            ("Ganancia Potencial", 16, "center"),
            ("% del Total",        10, "center"),
        ])
        tf3.grid(row=1, column=0, sticky="nsew",
                 padx=e(8), pady=(0, e(4)))
        self.lbl_val_total = tk.Label(
            tab3, text="",
            font=("Segoe UI", fs(11), "bold"),
            bg=C["fondo"], fg=C["naranja"],
            anchor="center", wraplength=900)
        self.lbl_val_total.grid(row=2, column=0,
                                 sticky="ew", padx=e(10), pady=e(6))
        self._cargar_valor_cat()

        # ── Tab 4: Productos críticos ─────────────────────────────
        tab4 = tk.Frame(nb, bg=C["fondo"])
        tab4.rowconfigure(2, weight=1)
        tab4.columnconfigure(0, weight=1)
        nb.add(tab4, text="  ⚠  Productos Críticos  ")

        tk.Label(tab4,
                 text="Productos que requieren reposición inmediata",
                 font=("Segoe UI", fs(11)),
                 bg=C["fondo"], fg=C["texto_gris"],
                 anchor="w").grid(
            row=0, column=0, sticky="ew",
            padx=e(12), pady=(e(10), e(2)))
        make_button(tab4, "🔄  Actualizar",
                    lambda: self._cargar_criticos(),
                    pad=e(6)).grid(
            row=1, column=0, sticky="w",
            padx=e(10), pady=(0, e(4)))
        tf4, self.tree_crit = make_treeview(tab4, [
            ("Código",     9, "center"),
            ("Producto",  22, "w"),
            ("Categoría", 13, "center"),
            ("Stock",      7, "center"),
            ("Mínimo",     7, "center"),
            ("Déficit",    7, "center"),
            ("Estado",    10, "center"),
        ])
        tf4.grid(row=2, column=0, sticky="nsew",
                 padx=e(8), pady=(0, e(8)))
        self._cargar_criticos()

    def _cargar_resumen(self):
        for w in self.frame_kpi.winfo_children():
            w.destroy()

        conn, cur = db_connect()
        cur.execute("SELECT COUNT(*) FROM productos")
        n_prod = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM categorias")
        n_cats = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo")
        n_bajo = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM productos WHERE stock = 0")
        n_agot = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(stock*precio_compra),0) FROM productos")
        val_c  = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(stock*precio_venta),0) FROM productos")
        val_v  = cur.fetchone()[0]
        conn.close()

        kpis = [
            ("Productos\nRegistrados", str(n_prod),             C["btn_secundario"]),
            ("Categorías",             str(n_cats),             C["naranja"]),
            ("Stock Bajo\no Agotado",  str(n_bajo),             C["btn_peligro"]),
            ("Productos\nAgotados",    str(n_agot),             "#8E1B0E"),
            ("Capital\nInvertido",     f"Q {val_c:,.0f}",       C["naranja_oscuro"]),
            ("Ganancia\nPotencial",    f"Q {val_v-val_c:,.0f}", C["btn_exito"]),
        ]

        for col in range(3):
            self.frame_kpi.columnconfigure(col, weight=1)
        for row in range(2):
            self.frame_kpi.rowconfigure(row, weight=1)

        for i, (titulo, valor, color) in enumerate(kpis):
            card = tk.Frame(self.frame_kpi, bg=color)
            card.grid(row=i // 3, column=i % 3,
                      padx=e(10), pady=e(10), sticky="nsew")

            tk.Label(card, text=valor,
                     font=("Segoe UI", fs(26), "bold"),
                     bg=color, fg="white").pack(
                expand=True, pady=(e(16), e(4)))
            tk.Label(card, text=titulo,
                     font=("Segoe UI", fs(10)),
                     bg=color, fg="#FFE0C0",
                     justify="center").pack(pady=(0, e(14)))

    def _cargar_por_cat(self):
        limpiar_tree(self.tree_cat)
        conn, cur = db_connect()
        cur.execute("""
            SELECT COALESCE(c.nombre,'Sin categoría'),
                   COUNT(p.id),
                   COALESCE(SUM(p.stock),0),
                   COALESCE(AVG(p.precio_venta),0)
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            GROUP BY c.nombre ORDER BY COUNT(p.id) DESC
        """)
        for r in cur.fetchall():
            insertar_fila(self.tree_cat,
                (r[0], r[1], r[2], f"Q {r[3]:,.2f}"))
        conn.close()

    def _cargar_valor_cat(self):
        limpiar_tree(self.tree_val_cat)
        conn, cur = db_connect()
        cur.execute("""
            SELECT COALESCE(c.nombre,'Sin cat.'),
                   COALESCE(SUM(p.stock*p.precio_compra),0),
                   COALESCE(SUM(p.stock*p.precio_venta),0)
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            GROUP BY c.nombre
            ORDER BY SUM(p.stock*p.precio_venta) DESC
        """)
        rows = cur.fetchall(); conn.close()
        tv_total = sum(r[2] for r in rows) or 1
        tc_total = sum(r[1] for r in rows)
        for r in rows:
            co = r[1]; ve = r[2]
            insertar_fila(self.tree_val_cat,
                (r[0], f"Q {co:,.2f}", f"Q {ve:,.2f}",
                 f"Q {ve-co:,.2f}", f"{ve/tv_total*100:.1f}%"))
        self.lbl_val_total.config(
            text=(f"Total invertido: Q {tc_total:,.2f}     │     "
                  f"Valor total de venta: Q {tv_total:,.2f}"))

    def _cargar_criticos(self):
        limpiar_tree(self.tree_crit)
        conn, cur = db_connect()
        cur.execute("""
            SELECT p.codigo, p.nombre, COALESCE(c.nombre,'—'),
                   p.stock, p.stock_minimo,
                   (p.stock_minimo - p.stock) AS deficit
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.stock <= p.stock_minimo
            ORDER BY p.stock ASC, p.nombre
        """)
        for r in cur.fetchall():
            insertar_fila(self.tree_crit,
                (r[0], r[1], r[2], r[3], r[4], r[5],
                 "🔴 AGOTADO" if r[3] == 0 else "🟡 BAJO"),
                tag="alerta")
        conn.close()

    def cargar(self):
        self._cargar_resumen()


# ════════════════════════════════════════════════════════════════
#  MÓDULO DE VENTAS
# ════════════════════════════════════════════════════════════════

class PanelVentas(tk.Frame):
    """
    Módulo completo de registro de ventas.

    LAYOUT:
    ┌──────────────────────┬──────────────────────────────────┐
    │   NUEVA VENTA        │   HISTORIAL DE VENTAS            │
    │                      │                                  │
    │  Cliente             │  Tabla de ventas registradas     │
    │  ──────────────────  │  con número, fecha, cliente      │
    │  Agregar producto    │  y total.                        │
    │  [código] [cantidad] │                                  │
    │  [Agregar al carrito]│  Botón: Ver detalle de venta     │
    │                      │  seleccionada                    │
    │  CARRITO             │                                  │
    │  ────────────────    │                                  │
    │  tabla de ítems      │                                  │
    │  [Quitar ítem]       │                                  │
    │                      │                                  │
    │  TOTAL: Q xxx.xx     │                                  │
    │  [Confirmar Venta]   │                                  │
    └──────────────────────┴──────────────────────────────────┘

    LÓGICA DE NEGOCIO:
    • Cada venta tiene un número único (V-00001, V-00002…)
    • Al confirmar: se insertan registros en ventas y detalle_ventas
    • El stock de cada producto se descuenta automáticamente
    • Si no hay stock suficiente no se puede agregar al carrito
    """

    def __init__(self, parent):
        super().__init__(parent, bg=C["fondo"])
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.carrito = []          # Lista de dicts con los ítems en curso
        self._build()

    # ──────────────────────────────────────────────────────────
    #  CONSTRUCCIÓN DEL PANEL
    # ──────────────────────────────────────────────────────────
    def _build(self):
        hacer_header(self, "🧾  VENTAS")

        # Contenedor principal dividido en 2 columnas
        main = tk.Frame(self, bg=C["fondo"])
        main.grid(row=1, column=0, sticky="nsew",
                  padx=e(12), pady=e(10))
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=4, minsize=e(340))
        main.columnconfigure(1, weight=6)

        self._build_panel_izq(main)
        self._build_panel_der(main)

    # ── Panel izquierdo: formulario de nueva venta ─────────────
    def _build_panel_izq(self, parent):
        izq = tk.Frame(parent, bg=C["fondo"],
                       highlightthickness=1,
                       highlightbackground=C["borde"])
        izq.grid(row=0, column=0, sticky="nsew",
                 padx=(0, e(8)))
        izq.rowconfigure(4, weight=1)    # fila del carrito se expande
        izq.columnconfigure(0, weight=1)

        # ── Título sección ───────────────────────────────────────
        sec_hdr = tk.Frame(izq, bg=C["naranja_oscuro"])
        sec_hdr.grid(row=0, column=0, sticky="ew")
        tk.Label(sec_hdr, text="  ➕  Nueva Venta",
                 font=("Segoe UI", fs(11), "bold"),
                 bg=C["naranja_oscuro"], fg="white",
                 pady=e(8)).pack(side="left")

        # ── Datos del cliente ────────────────────────────────────
        datos = tk.Frame(izq, bg=C["fondo"], padx=e(12), pady=e(8))
        datos.grid(row=1, column=0, sticky="ew")
        datos.columnconfigure(1, weight=1)

        tk.Label(datos, text="Cliente:",
                 font=("Segoe UI", fs(10), "bold"),
                 bg=C["fondo"]).grid(row=0, column=0,
                                     sticky="w", padx=(0, e(8)))
        self.ent_cliente = tk.Entry(
            datos, font=("Segoe UI", fs(11)),
            relief="flat",
            highlightthickness=1,
            highlightbackground=C["borde"],
            highlightcolor=C["naranja"])
        self.ent_cliente.grid(row=0, column=1, sticky="ew")
        self.ent_cliente.insert(0, "Público General")

        # ── Separador ────────────────────────────────────────────
        tk.Frame(izq, bg=C["borde"], height=1).grid(
            row=2, column=0, sticky="ew", padx=e(8))

        # ── Agregar producto al carrito ──────────────────────────
        agregar_frame = tk.Frame(izq, bg=C["fondo"],
                                  padx=e(12), pady=e(8))
        agregar_frame.grid(row=3, column=0, sticky="ew")
        agregar_frame.columnconfigure(1, weight=1)

        tk.Label(agregar_frame, text="Código producto:",
                 font=("Segoe UI", fs(10), "bold"),
                 bg=C["fondo"]).grid(row=0, column=0,
                                     sticky="w", padx=(0, e(8)), pady=e(4))
        self.ent_codigo = tk.Entry(
            agregar_frame, font=("Segoe UI", fs(11)),
            relief="flat",
            highlightthickness=1,
            highlightbackground=C["borde"],
            highlightcolor=C["naranja"])
        self.ent_codigo.grid(row=0, column=1, sticky="ew", pady=e(4))
        # Enter en código → busca el producto
        self.ent_codigo.bind("<Return>", lambda _: self.ent_cantidad.focus())

        tk.Label(agregar_frame, text="Cantidad:",
                 font=("Segoe UI", fs(10), "bold"),
                 bg=C["fondo"]).grid(row=1, column=0,
                                     sticky="w", padx=(0, e(8)), pady=e(4))
        self.ent_cantidad = tk.Entry(
            agregar_frame, font=("Segoe UI", fs(11)),
            width=8, relief="flat",
            highlightthickness=1,
            highlightbackground=C["borde"],
            highlightcolor=C["naranja"])
        self.ent_cantidad.grid(row=1, column=1, sticky="w", pady=e(4))
        self.ent_cantidad.insert(0, "1")
        # Enter en cantidad → agrega al carrito
        self.ent_cantidad.bind("<Return>", lambda _: self.agregar_al_carrito())

        make_button(agregar_frame, "🛒  Agregar al Carrito",
                    self.agregar_al_carrito).grid(
            row=2, column=0, columnspan=2,
            sticky="ew", pady=(e(6), 0))

        # ── Carrito ──────────────────────────────────────────────
        carrito_hdr = tk.Frame(izq, bg=C["header_bg"])
        carrito_hdr.grid(row=4, column=0, sticky="new", pady=(e(6), 0))
        tk.Label(carrito_hdr, text="  🧺  Carrito",
                 font=("Segoe UI", fs(10), "bold"),
                 bg=C["header_bg"], fg="white",
                 pady=e(6)).pack(side="left")

        # Tabla del carrito
        carrito_tabla = tk.Frame(izq, bg=C["fondo"])
        carrito_tabla.grid(row=4, column=0, sticky="nsew",
                            padx=e(8), pady=(e(26), 0))
        carrito_tabla.rowconfigure(0, weight=1)
        carrito_tabla.columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Car.Treeview.Heading",
                        background=C["header_bg"],
                        foreground="white",
                        font=("Segoe UI", fs(9), "bold"),
                        relief="flat")
        style.configure("Car.Treeview",
                        font=("Segoe UI", fs(10)),
                        rowheight=e(28),
                        background="#FFFFFF",
                        fieldbackground="#FFFFFF")
        style.map("Car.Treeview",
                  background=[("selected", C["tabla_seleccion"])],
                  foreground=[("selected", C["texto"])])

        self.tree_carrito = ttk.Treeview(
            carrito_tabla,
            columns=("Código", "Producto", "Cant.", "P.Unit", "Subtotal"),
            show="headings",
            style="Car.Treeview")
        for col, w, anc in [
            ("Código",   e(80),  "center"),
            ("Producto", e(140), "w"),
            ("Cant.",    e(45),  "center"),
            ("P.Unit",   e(75),  "center"),
            ("Subtotal", e(80),  "center"),
        ]:
            self.tree_carrito.heading(col, text=col)
            self.tree_carrito.column(col, width=w, anchor=anc, stretch=True)

        vsb = ttk.Scrollbar(carrito_tabla, orient="vertical",
                             command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=vsb.set)
        self.tree_carrito.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        # Botón quitar ítem
        make_button(izq, "✖  Quitar ítem seleccionado",
                    self.quitar_item,
                    color=C["btn_peligro"]).grid(
            row=5, column=0, sticky="ew",
            padx=e(8), pady=(e(4), 0))

        # ── Total + Confirmar ────────────────────────────────────
        total_frame = tk.Frame(izq, bg=C["naranja_oscuro"])
        total_frame.grid(row=6, column=0, sticky="ew",
                          padx=0, pady=(e(6), 0))
        total_frame.columnconfigure(0, weight=1)

        self.lbl_total = tk.Label(
            total_frame,
            text="TOTAL:  Q 0.00",
            font=("Segoe UI", fs(14), "bold"),
            bg=C["naranja_oscuro"], fg="white",
            pady=e(10))
        self.lbl_total.pack()

        make_button(izq, "✔  CONFIRMAR VENTA",
                    self.confirmar_venta,
                    color=C["btn_exito"],
                    pad=e(10)).grid(
            row=7, column=0, sticky="ew",
            padx=e(8), pady=e(8))

    # ── Panel derecho: historial de ventas ──────────────────────
    def _build_panel_der(self, parent):
        der = tk.Frame(parent, bg=C["fondo"],
                       highlightthickness=1,
                       highlightbackground=C["borde"])
        der.grid(row=0, column=1, sticky="nsew")
        der.rowconfigure(1, weight=1)
        der.columnconfigure(0, weight=1)

        # Encabezado
        sec_hdr = tk.Frame(der, bg=C["header_bg"])
        sec_hdr.grid(row=0, column=0, sticky="ew")
        tk.Label(sec_hdr, text="  📋  Historial de Ventas",
                 font=("Segoe UI", fs(11), "bold"),
                 bg=C["header_bg"], fg="white",
                 pady=e(8)).pack(side="left")

        # Tabla historial
        tf, self.tree_ventas = make_treeview(der, [
            ("# Venta",  9,  "center"),
            ("Fecha",    14, "center"),
            ("Cliente",  18, "w"),
            ("Items",     6, "center"),
            ("Total",    10, "center"),
            ("Estado",    9, "center"),
        ])
        tf.grid(row=1, column=0, sticky="nsew",
                padx=e(8), pady=e(8))

        # Botones del historial
        btns = tk.Frame(der, bg=C["fondo"], pady=e(6))
        btns.grid(row=2, column=0, sticky="ew", padx=e(8))

        make_button(btns, "🔍  Ver Detalle",
                    self.ver_detalle_venta,
                    color=C["btn_secundario"]).pack(side="left", padx=(0, e(6)))
        make_button(btns, "🔄  Actualizar",
                    self.cargar_historial).pack(side="left")

    # ──────────────────────────────────────────────────────────
    #  LÓGICA DEL CARRITO
    # ──────────────────────────────────────────────────────────
    def agregar_al_carrito(self):
        """
        Busca el producto por código, valida stock,
        y lo agrega a la lista del carrito.
        Si el mismo código ya está en el carrito, suma la cantidad.
        """
        codigo  = self.ent_codigo.get().strip().upper()
        try:
            cantidad = int(self.ent_cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error",
                "La cantidad debe ser un número entero mayor a 0.")
            return

        if not codigo:
            messagebox.showerror("Error", "Ingresa el código del producto.")
            return

        # Buscar producto en BD
        conn, cur = db_connect()
        cur.execute(
            "SELECT id, nombre, precio_venta, stock FROM productos WHERE codigo=?",
            (codigo,))
        prod = cur.fetchone()
        conn.close()

        if not prod:
            messagebox.showerror("Producto no encontrado",
                f"No existe ningún producto con el código '{codigo}'.")
            return

        prod_id  = prod[0]
        nombre   = prod[1]
        precio   = prod[2]
        stock_db = prod[3]

        # Calcular cuánto ya hay en el carrito de este producto
        ya_en_carrito = sum(
            item["cantidad"] for item in self.carrito
            if item["codigo"] == codigo)

        total_pedido = ya_en_carrito + cantidad

        if total_pedido > stock_db:
            disponible = stock_db - ya_en_carrito
            messagebox.showwarning("Stock insuficiente",
                f"Stock disponible: {stock_db} uds.\n"
                f"Ya en carrito:    {ya_en_carrito} uds.\n"
                f"Puedes agregar:   {max(0, disponible)} uds. más.")
            return

        # Si ya existe en el carrito → sumar cantidad
        for item in self.carrito:
            if item["codigo"] == codigo:
                item["cantidad"] += cantidad
                item["subtotal"]  = item["cantidad"] * item["precio_unit"]
                self._refrescar_carrito()
                self.ent_codigo.delete(0, "end")
                self.ent_cantidad.delete(0, "end")
                self.ent_cantidad.insert(0, "1")
                self.ent_codigo.focus()
                return

        # Producto nuevo en el carrito
        self.carrito.append({
            "codigo":     codigo,
            "prod_id":    prod_id,
            "nombre":     nombre,
            "cantidad":   cantidad,
            "precio_unit": precio,
            "subtotal":   cantidad * precio,
        })

        self._refrescar_carrito()
        self.ent_codigo.delete(0, "end")
        self.ent_cantidad.delete(0, "end")
        self.ent_cantidad.insert(0, "1")
        self.ent_codigo.focus()

    def quitar_item(self):
        """Elimina el ítem seleccionado del carrito."""
        sel = self.tree_carrito.selection()
        if not sel:
            messagebox.showinfo("Selecciona",
                "Haz clic en un ítem del carrito primero.")
            return
        idx = self.tree_carrito.index(sel[0])
        self.carrito.pop(idx)
        self._refrescar_carrito()

    def _refrescar_carrito(self):
        """Redibuja la tabla del carrito y actualiza el total."""
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)

        total = 0.0
        for i, item in enumerate(self.carrito):
            tag = "par" if i % 2 == 0 else "impar"
            self.tree_carrito.insert("", "end", tags=(tag,), values=(
                item["codigo"],
                item["nombre"],
                item["cantidad"],
                f"Q {item['precio_unit']:,.2f}",
                f"Q {item['subtotal']:,.2f}",
            ))
            total += item["subtotal"]

        self.lbl_total.config(text=f"TOTAL:   Q {total:,.2f}")

    # ──────────────────────────────────────────────────────────
    #  CONFIRMAR VENTA
    # ──────────────────────────────────────────────────────────
    def confirmar_venta(self):
        """
        Guarda la venta completa en la base de datos.

        Pasos:
        1. Validar que el carrito no esté vacío
        2. Generar número de venta correlativo (V-00001, V-00002…)
        3. Insertar registro en tabla 'ventas'
        4. Insertar cada ítem en tabla 'detalle_ventas'
        5. Descontar stock de cada producto
        6. Limpiar el carrito para la siguiente venta
        """
        if not self.carrito:
            messagebox.showwarning("Carrito vacío",
                "Agrega al menos un producto antes de confirmar.")
            return

        cliente = self.ent_cliente.get().strip() or "Público General"
        total   = sum(item["subtotal"] for item in self.carrito)
        fecha   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Confirmación
        if not messagebox.askyesno("Confirmar Venta",
            f"Cliente: {cliente}\n"
            f"Ítems:   {len(self.carrito)}\n"
            f"Total:   Q {total:,.2f}\n\n"
            "¿Registrar esta venta?"):
            return

        conn, cur = db_connect()
        try:
            # Número correlativo
            cur.execute("SELECT COUNT(*) FROM ventas")
            n = cur.fetchone()[0] + 1
            numero = f"V-{n:05d}"

            # Insertar cabecera de venta
            cur.execute("""
                INSERT INTO ventas (numero, cliente, fecha, total, estado)
                VALUES (?, ?, ?, ?, 'completada')
            """, (numero, cliente, fecha, total))
            venta_id = cur.lastrowid

            # Insertar ítems y descontar stock
            for item in self.carrito:
                cur.execute("""
                    INSERT INTO detalle_ventas
                    (venta_id, producto_id, codigo, nombre,
                     cantidad, precio_unit, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (venta_id, item["prod_id"], item["codigo"],
                      item["nombre"], item["cantidad"],
                      item["precio_unit"], item["subtotal"]))

                cur.execute(
                    "UPDATE productos SET stock = stock - ? WHERE id = ?",
                    (item["cantidad"], item["prod_id"]))

            conn.commit()
            messagebox.showinfo("✔ Venta Registrada",
                f"Venta {numero} registrada correctamente.\n"
                f"Total: Q {total:,.2f}")

            # Limpiar para la siguiente venta
            self.carrito.clear()
            self._refrescar_carrito()
            self.ent_cliente.delete(0, "end")
            self.ent_cliente.insert(0, "Público General")
            self.ent_codigo.delete(0, "end")
            self.cargar_historial()

        except Exception as ex:
            conn.rollback()
            messagebox.showerror("Error al registrar",
                f"Ocurrió un error:\n{ex}")
        finally:
            conn.close()

    # ──────────────────────────────────────────────────────────
    #  HISTORIAL
    # ──────────────────────────────────────────────────────────
    def cargar_historial(self):
        """Recarga la tabla del historial con todas las ventas."""
        limpiar_tree(self.tree_ventas)
        conn, cur = db_connect()
        cur.execute("""
            SELECT v.numero, v.fecha, v.cliente,
                   COUNT(d.id) AS items,
                   v.total, v.estado
            FROM ventas v
            LEFT JOIN detalle_ventas d ON d.venta_id = v.id
            GROUP BY v.id
            ORDER BY v.id DESC
        """)
        for r in cur.fetchall():
            insertar_fila(self.tree_ventas, (
                r[0], r[1], r[2], r[3],
                f"Q {r[4]:,.2f}", r[5].capitalize()
            ))
        conn.close()

    def ver_detalle_venta(self):
        """
        Abre una ventana modal con el detalle completo
        de la venta seleccionada en el historial.
        """
        sel = self.tree_ventas.selection()
        if not sel:
            messagebox.showinfo("Selecciona",
                "Haz clic en una venta del historial primero.")
            return

        vals   = self.tree_ventas.item(sel[0])["values"]
        numero = vals[0]
        fecha  = vals[1]
        cliente= vals[2]
        total  = vals[4]

        # Consultar ítems del detalle
        conn, cur = db_connect()
        cur.execute("""
            SELECT codigo, nombre, cantidad, precio_unit, subtotal
            FROM detalle_ventas
            WHERE venta_id = (SELECT id FROM ventas WHERE numero=?)
            ORDER BY id
        """, (numero,))
        items = cur.fetchall()
        conn.close()

        # Ventana de detalle
        dlg = tk.Toplevel(self.winfo_toplevel())
        dlg.title(f"Detalle — {numero}")
        dlg.configure(bg=C["fondo"])
        dlg.resizable(True, True)
        dlg.minsize(e(500), e(350))
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        # Centrar
        dlg.update_idletasks()
        w, h = e(640), e(480)
        x = (dlg.winfo_screenwidth()  // 2) - (w // 2)
        y = (dlg.winfo_screenheight() // 2) - (h // 2)
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        # Encabezado
        hdr = tk.Frame(dlg, bg=C["naranja"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"  Detalle de Venta — {numero}",
                 font=("Segoe UI", fs(13), "bold"),
                 bg=C["naranja"], fg="white",
                 pady=e(11)).pack(side="left")

        # Info general
        info = tk.Frame(dlg, bg=C["fondo"], padx=e(16), pady=e(10))
        info.pack(fill="x")
        for etq, val in [("Fecha:", fecha),
                          ("Cliente:", cliente),
                          ("Total:", total)]:
            row = tk.Frame(info, bg=C["fondo"])
            row.pack(anchor="w")
            tk.Label(row, text=etq,
                     font=("Segoe UI", fs(10), "bold"),
                     bg=C["fondo"], width=10, anchor="w").pack(side="left")
            tk.Label(row, text=val,
                     font=("Segoe UI", fs(10)),
                     bg=C["fondo"]).pack(side="left")

        tk.Frame(dlg, bg=C["borde"], height=1).pack(fill="x", padx=e(12))

        # Tabla de ítems
        det_frame = tk.Frame(dlg, bg=C["fondo"])
        det_frame.pack(fill="both", expand=True,
                       padx=e(12), pady=e(10))
        det_frame.rowconfigure(0, weight=1)
        det_frame.columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Det.Treeview.Heading",
                        background=C["tabla_header"],
                        foreground="white",
                        font=("Segoe UI", fs(10), "bold"),
                        relief="flat")
        style.configure("Det.Treeview",
                        font=("Segoe UI", fs(10)),
                        rowheight=e(28))

        det_tree = ttk.Treeview(
            det_frame,
            columns=("Código", "Producto", "Cant.", "P.Unit", "Subtotal"),
            show="headings",
            style="Det.Treeview")
        for col, ancho, anc in [
            ("Código",   e(90),  "center"),
            ("Producto", e(200), "w"),
            ("Cant.",    e(55),  "center"),
            ("P.Unit",   e(90),  "center"),
            ("Subtotal", e(90),  "center"),
        ]:
            det_tree.heading(col, text=col)
            det_tree.column(col, width=ancho, anchor=anc, stretch=True)

        vsb = ttk.Scrollbar(det_frame, orient="vertical",
                             command=det_tree.yview)
        det_tree.configure(yscrollcommand=vsb.set)
        det_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        det_tree.tag_configure("par",   background=C["tabla_fila1"])
        det_tree.tag_configure("impar", background=C["tabla_fila2"])

        for i, r in enumerate(items):
            tag = "par" if i % 2 == 0 else "impar"
            det_tree.insert("", "end", tags=(tag,), values=(
                r[0], r[1], r[2],
                f"Q {r[3]:,.2f}",
                f"Q {r[4]:,.2f}",
            ))

        # Botón cerrar
        make_button(dlg, "Cerrar", dlg.destroy,
                    color=C["btn_secundario"]).pack(pady=e(10))

    def cargar(self):
        """Recarga el historial al entrar al módulo."""
        self.cargar_historial()


# ════════════════════════════════════════════════════════════════
#  SIDEBAR COLAPSABLE
# ════════════════════════════════════════════════════════════════

class Sidebar(tk.Frame):
    EXPANDIDO = int(215 * max(1.0, 1.0))   # se recalcula con ESCALA en __init__
    COLAPSADO = int(55  * max(1.0, 1.0))

    def __init__(self, parent, on_select, on_toggle=None):
        self.EXPANDIDO = e(215)
        self.COLAPSADO = e(55)
        super().__init__(parent, bg=C["sidebar_bg"],
                         width=self.EXPANDIDO)
        self.pack_propagate(False)
        self.on_select  = on_select
        self.on_toggle  = on_toggle
        self.botones    = {}
        self.activo     = None
        self.expandido  = True
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=C["naranja"])
        top.pack(fill="x")

        self.logo_frame = tk.Frame(top, bg=C["naranja"])
        self.logo_frame.pack(side="left", expand=True, fill="both",
                              pady=e(4))

        self.lbl_titulo = tk.Label(
            self.logo_frame, text="🔧 FERRETERÍA",
            font=("Segoe UI", fs(12), "bold"),
            bg=C["naranja"], fg="white")
        self.lbl_titulo.pack(pady=(e(13), e(2)))

        self.lbl_sub = tk.Label(
            self.logo_frame, text="Sistema de Gestión",
            font=("Segoe UI", fs(8)),
            bg=C["naranja"], fg="#FFD4A8")
        self.lbl_sub.pack()

        self.btn_toggle = tk.Button(
            top, text="✕",
            font=("Segoe UI", fs(13), "bold"),
            bg=C["naranja"], fg="white",
            relief="flat", cursor="hand2",
            activebackground=C["naranja_oscuro"],
            activeforeground="white",
            bd=0, padx=e(8),
            command=self.toggle)
        self.btn_toggle.pack(side="right", padx=e(4), pady=e(4))

        tk.Frame(self, bg=C["naranja"], height=2).pack(fill="x")

        self.items_info = [
            ("📦", "Productos",  "productos"),
            ("⚙",  "Categorías", "categorias"),
            ("🗂",  "Inventario", "inventario"),
            ("🧾", "Ventas",     "ventas"),
            ("📊", "Reportes",   "reportes"),
        ]

        for icono, texto, clave in self.items_info:
            btn = tk.Button(
                self,
                text=f"  {icono}  {texto}",
                font=("Segoe UI", fs(11)),
                bg=C["sidebar_bg"], fg="#CCCCCC",
                activebackground=C["naranja"],
                activeforeground="white",
                relief="flat", anchor="w",
                cursor="hand2",
                padx=e(10), pady=e(13),
                command=lambda k=clave: self.seleccionar(k))
            btn.pack(fill="x")

            def on_enter(ev, b=btn, k=clave):
                if self.activo != k:
                    b.config(bg=C["sidebar_hover"], fg="white")
            def on_leave(ev, b=btn, k=clave):
                if self.activo != k:
                    b.config(bg=C["sidebar_bg"], fg="#CCCCCC")
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            self.botones[clave] = btn

        pie = tk.Frame(self, bg=C["sidebar_bg"])
        pie.pack(side="bottom", fill="x")
        tk.Frame(pie, bg="#444444", height=1).pack(fill="x")
        self.lbl_version = tk.Label(
            pie, text="v1.0 — Python + Tkinter",
            font=("Segoe UI", fs(8)),
            bg=C["sidebar_bg"], fg="#666666")
        self.lbl_version.pack(pady=e(9))

    def toggle(self):
        if self.expandido:
            self.config(width=self.COLAPSADO)
            self.btn_toggle.config(text="☰")
            self.lbl_titulo.pack_forget()
            self.lbl_sub.pack_forget()
            self.lbl_version.pack_forget()
            for icono, _, clave in self.items_info:
                self.botones[clave].config(
                    text=icono,
                    font=("Segoe UI", fs(16)),
                    padx=0, anchor="center")
            self.expandido = False
        else:
            self.config(width=self.EXPANDIDO)
            self.btn_toggle.config(text="✕")
            self.lbl_titulo.pack(in_=self.logo_frame, pady=(e(13), e(2)))
            self.lbl_sub.pack(in_=self.logo_frame)
            self.lbl_version.pack(pady=e(9))
            for icono, texto, clave in self.items_info:
                self.botones[clave].config(
                    text=f"  {icono}  {texto}",
                    font=("Segoe UI", fs(11)),
                    padx=e(10), anchor="w")
            self.expandido = True
        if self.on_toggle:
            self.on_toggle()

    def seleccionar(self, clave):
        if self.activo and self.activo in self.botones:
            self.botones[self.activo].config(
                bg=C["sidebar_bg"], fg="#CCCCCC")
        self.activo = clave
        self.botones[clave].config(bg=C["naranja"], fg="white")
        self.on_select(clave)


# ════════════════════════════════════════════════════════════════
#  APLICACIÓN PRINCIPAL
# ════════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🔧 Ferretería — Sistema de Gestión")
        self.configure(bg=C["fondo"])

        # Tamaño inicial: 80% de la pantalla, completamente redimensionable
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        ancho = int(sw * 0.80)
        alto  = int(sh * 0.82)
        self.minsize(e(800), e(520))

        x = (sw // 2) - (ancho // 2)
        y = (sh // 2) - (alto  // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

        db_init()

        # Sidebar
        self.sidebar = Sidebar(self, self.mostrar_panel,
                               on_toggle=lambda: self.update_idletasks())
        self.sidebar.pack(side="left", fill="y")

        # Área de contenido — usa grid para que sticky="nsew" funcione
        self.area = tk.Frame(self, bg=C["fondo"])
        self.area.pack(side="left", fill="both", expand=True)
        self.area.rowconfigure(0, weight=1)
        self.area.columnconfigure(0, weight=1)

        self.paneles = {
            "productos":  PanelProductos(self.area),
            "categorias": PanelCategorias(self.area),
            "inventario": PanelInventario(self.area),
            "ventas":     PanelVentas(self.area),
            "reportes":   PanelReportes(self.area),
        }

        self.panel_actual = None
        self.sidebar.seleccionar("productos")

    def mostrar_panel(self, clave):
        if self.panel_actual:
            self.paneles[self.panel_actual].grid_remove()
        self.paneles[clave].grid(row=0, column=0, sticky="nsew")
        self.panel_actual = clave
        if hasattr(self.paneles[clave], "cargar"):
            self.paneles[clave].cargar()


# ════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
