"""
╔══════════════════════════════════════════════════════════════════╗
║           FERRETERÍA — SISTEMA DE GESTIÓN (CÓDIGO BASE)          ║
║        Módulos: 1-Productos · 3-Inventario · 5-Reportes          ║
║                     Versión consola Python                        ║
╚══════════════════════════════════════════════════════════════════╝

CÓMO EJECUTAR:
    python ferreteria.py

LIBRERÍAS NECESARIAS:
    pip install tabulate colorama
"""

# ─────────────────────────────────────────────────────────────────
# PASO 1 — IMPORTAR LIBRERÍAS
# ─────────────────────────────────────────────────────────────────
# Importar = traer herramientas que ya existen para usarlas aquí

import sqlite3                          # Manejo de base de datos local
import os                               # Limpiar pantalla
from datetime import datetime           # Capturar fecha y hora actual
from tabulate import tabulate           # Mostrar tablas bonitas en consola
from colorama import init, Fore, Style  # Colores en el texto de consola

# Activar colorama (necesario en Windows para que los colores funcionen)
init(autoreset=True)


# ─────────────────────────────────────────────────────────────────
# PASO 2 — BASE DE DATOS
# ─────────────────────────────────────────────────────────────────

ARCHIVO_DB = "ferreteria.db"
# Este archivo se crea automáticamente en la misma carpeta del programa.
# Guarda todo: categorías, productos. Es como el archivo de Excel del negocio.


def conectar():
    """
    Abre la conexión con la base de datos y la retorna.
    Es como abrir el libro contable antes de anotar algo.
    """
    return sqlite3.connect(ARCHIVO_DB)


def crear_tablas():
    """
    Crea las tablas si no existen. Se ejecuta una sola vez al iniciar.

    TABLA categorias:
      id          → número único automático (1, 2, 3...)
      nombre      → ej: "Herramientas" (no puede repetirse: UNIQUE)
      descripcion → texto opcional

    TABLA productos:
      id             → número único automático
      codigo         → ej: MART-001 (no puede repetirse: UNIQUE)
      nombre         → ej: "Martillo 16 oz"
      descripcion    → detalles opcionales
      precio_compra  → cuánto pagó la ferretería al proveedor
      precio_venta   → cuánto cobra la ferretería al cliente
      stock          → cuántas unidades hay en bodega ahora
      stock_minimo   → si el stock baja de aquí, aparece una alerta
      categoria_id   → número que apunta a qué categoría pertenece
      fecha_registro → cuándo se registró el producto
    """
    conn   = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL UNIQUE,
            descripcion TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo         TEXT NOT NULL UNIQUE,
            nombre         TEXT NOT NULL,
            descripcion    TEXT,
            precio_compra  REAL NOT NULL DEFAULT 0,
            precio_venta   REAL NOT NULL DEFAULT 0,
            stock          INTEGER NOT NULL DEFAULT 0,
            stock_minimo   INTEGER NOT NULL DEFAULT 5,
            categoria_id   INTEGER,
            fecha_registro TEXT,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    """)

    conn.commit()  # Confirmar y guardar los cambios
    conn.close()   # Cerrar la conexión (liberar recursos)


# ─────────────────────────────────────────────────────────────────
# PASO 3 — FUNCIONES DE UTILIDAD
# Herramientas pequeñas que se usan en todo el programa
# ─────────────────────────────────────────────────────────────────

def limpiar_pantalla():
    """Borra el texto de la consola. 'cls' = Windows, 'clear' = Mac/Linux"""
    os.system('cls' if os.name == 'nt' else 'clear')


def pausar():
    """Pausa el programa hasta que el usuario presione Enter."""
    input(f"\n{Fore.YELLOW}  Presiona Enter para continuar...{Style.RESET_ALL}")


def mostrar_titulo(texto):
    """Imprime un título con líneas decorativas."""
    print(f"\n{Fore.CYAN}{'═' * 55}")
    print(f"  {texto}")
    print(f"{'═' * 55}{Style.RESET_ALL}\n")


def mensaje_exito(texto):
    """Texto en verde con palomita ✔"""
    print(f"\n  {Fore.GREEN}✔  {texto}{Style.RESET_ALL}")


def mensaje_error(texto):
    """Texto en rojo con X ✘"""
    print(f"\n  {Fore.RED}✘  {texto}{Style.RESET_ALL}")


def mensaje_alerta(texto):
    """Texto en amarillo con ⚠"""
    print(f"\n  {Fore.YELLOW}⚠  {texto}{Style.RESET_ALL}")


def obtener_lista_categorias():
    """
    Función auxiliar: retorna las categorías como lista de tuplas [(id, nombre)].
    Se usa cuando otro módulo necesita mostrar las categorías disponibles.
    """
    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
    resultado = cursor.fetchall()
    conn.close()
    return resultado


# ═════════════════════════════════════════════════════════════════
#  MÓDULO 1A — CATEGORÍAS
#  Las categorías agrupan los productos en familias.
#  Ejemplos: Herramientas, Plomería, Tornillería, Eléctrico...
# ═════════════════════════════════════════════════════════════════

def menu_categorias():
    """
    Submenú de categorías.
    Es un bucle while que muestra opciones hasta que el usuario elige salir.
    """
    while True:
        limpiar_pantalla()
        mostrar_titulo("MÓDULO 1 → CATEGORÍAS")
        print("  [1] Agregar nueva categoría")
        print("  [2] Ver todas las categorías")
        print("  [0] Volver al menú principal")

        opcion = input(f"\n{Fore.CYAN}  Elige una opción: {Style.RESET_ALL}").strip()

        if opcion == "1":
            agregar_categoria()
        elif opcion == "2":
            ver_categorias()
        elif opcion == "0":
            break       # Salir del bucle y regresar al menú principal
        else:
            mensaje_error("Opción no válida.")
        pausar()


def agregar_categoria():
    """
    Pide nombre y descripción, y guarda la nueva categoría en la BD.

    SQL usado:
      INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)
      → Inserta una nueva fila en la tabla.
      → Los ? se reemplazan con los valores del usuario (evita hacking).
    """
    mostrar_titulo("NUEVA CATEGORÍA")

    nombre = input("  Nombre de la categoría: ").strip()
    if not nombre:
        mensaje_error("El nombre no puede estar vacío.")
        return

    descripcion = input("  Descripción (opcional, Enter para omitir): ").strip()

    try:
        conn   = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)",
            (nombre, descripcion)
        )
        conn.commit()
        conn.close()
        mensaje_exito(f"Categoría '{nombre}' registrada correctamente.")

    except sqlite3.IntegrityError:
        # IntegrityError = nombre repetido (la columna tiene restricción UNIQUE)
        mensaje_error(f"La categoría '{nombre}' ya existe.")


def ver_categorias():
    """
    Lee todas las categorías y las muestra en tabla.

    SQL usado:
      SELECT id, nombre, descripcion FROM categorias ORDER BY nombre
      → Lee todas las filas.
      → ORDER BY nombre = orden alfabético.
    """
    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, descripcion FROM categorias ORDER BY nombre")
    filas = cursor.fetchall()   # fetchall() = traer TODOS los resultados
    conn.close()

    mostrar_titulo("LISTADO DE CATEGORÍAS")
    if filas:
        print(tabulate(filas,
                       headers=["ID", "Nombre", "Descripción"],
                       tablefmt="rounded_outline"))
    else:
        mensaje_alerta("No hay categorías registradas.")


# ═════════════════════════════════════════════════════════════════
#  MÓDULO 1B — PRODUCTOS
#  El catálogo de todos los artículos de la ferretería.
# ═════════════════════════════════════════════════════════════════

def menu_productos():
    """Submenú de productos con todas las acciones disponibles."""
    while True:
        limpiar_pantalla()
        mostrar_titulo("MÓDULO 1 → PRODUCTOS")
        print("  [1] Registrar nuevo producto")
        print("  [2] Ver todos los productos")
        print("  [3] Buscar producto por nombre o código")
        print("  [4] Editar precio de un producto")
        print("  [5] Agregar stock (ingreso de mercancía)")
        print("  [0] Volver al menú principal")

        opcion = input(f"\n{Fore.CYAN}  Elige una opción: {Style.RESET_ALL}").strip()

        if opcion == "1":
            registrar_producto()
        elif opcion == "2":
            ver_productos()
        elif opcion == "3":
            buscar_producto()
        elif opcion == "4":
            editar_precio_producto()
        elif opcion == "5":
            agregar_stock_producto()
        elif opcion == "0":
            break
        else:
            mensaje_error("Opción no válida.")
        pausar()


def registrar_producto():
    """
    Pide todos los datos del producto y lo guarda en la base de datos.

    VALIDACIONES que hace:
      • Código y nombre no pueden estar vacíos
      • Precios y stock deben ser números (float/int)
      • La categoría elegida debe existir
      • El código no puede repetirse (UNIQUE en BD)
    """
    mostrar_titulo("REGISTRAR NUEVO PRODUCTO")

    # Verificar que exista al menos una categoría
    categorias = obtener_lista_categorias()
    if not categorias:
        mensaje_error("No hay categorías. Crea una primero en el Módulo Categorías.")
        return

    print("  Categorías disponibles:")
    for cat in categorias:
        print(f"    [{cat[0]}] {cat[1]}")

    try:
        print()
        codigo = input("  Código del producto (ej: MART-001): ").strip().upper()
        if not codigo:
            mensaje_error("El código no puede estar vacío.")
            return

        nombre = input("  Nombre del producto: ").strip()
        if not nombre:
            mensaje_error("El nombre no puede estar vacío.")
            return

        descripcion   = input("  Descripción (opcional): ").strip()
        precio_compra = float(input("  Precio de compra (Q): "))
        precio_venta  = float(input("  Precio de venta  (Q): "))
        stock         = int(input("  Stock inicial (unidades): "))
        stock_minimo  = int(input("  Stock mínimo para alerta: "))
        cat_id        = int(input("  ID de la categoría: "))

        # Verificar que el ID elegido existe en la lista
        ids_validos = [c[0] for c in categorias]
        if cat_id not in ids_validos:
            mensaje_error(f"El ID {cat_id} no corresponde a ninguna categoría.")
            return

        fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn   = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO productos
            (codigo, nombre, descripcion, precio_compra, precio_venta,
             stock, stock_minimo, categoria_id, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (codigo, nombre, descripcion, precio_compra, precio_venta,
              stock, stock_minimo, cat_id, fecha_hoy))
        conn.commit()
        conn.close()
        mensaje_exito(f"Producto '{nombre}' (código: {codigo}) registrado.")

    except ValueError:
        # float() o int() fallaron porque el usuario escribió texto en lugar de número
        mensaje_error("Precios y stock deben ser números (ej: 25.50 ó 10).")
    except sqlite3.IntegrityError:
        mensaje_error(f"El código '{codigo}' ya está registrado.")


def ver_productos():
    """
    Muestra todos los productos en tabla.

    SQL JOIN: une la tabla productos con categorias para mostrar
    el nombre de la categoría en vez del número (categoria_id).

    COALESCE(c.nombre, 'Sin categoría') → si no tiene categoría, muestra ese texto.
    """
    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.codigo, p.nombre,
               COALESCE(c.nombre, 'Sin categoría') AS categoria,
               p.precio_compra, p.precio_venta, p.stock, p.stock_minimo
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        ORDER BY p.nombre
    """)
    filas = cursor.fetchall()
    conn.close()

    mostrar_titulo("CATÁLOGO DE PRODUCTOS")
    if filas:
        tabla = []
        for f in filas:
            estado = f"{Fore.RED}⚠ BAJO{Style.RESET_ALL}" if f[5] <= f[6] else f"{Fore.GREEN}✔ OK{Style.RESET_ALL}"
            tabla.append([f[0], f[1], f[2], f"Q {f[3]:,.2f}", f"Q {f[4]:,.2f}", f[5], f[6], estado])

        print(tabulate(tabla,
                       headers=["Código", "Nombre", "Categoría",
                                 "P.Compra", "P.Venta", "Stock", "Mín.", "Estado"],
                       tablefmt="rounded_outline"))
        print(f"\n  Total: {Fore.CYAN}{len(filas)} productos{Style.RESET_ALL}")
    else:
        mensaje_alerta("No hay productos registrados.")


def buscar_producto():
    """
    Busca productos por nombre o código usando búsqueda parcial.

    SQL LIKE con comodines %:
      WHERE p.nombre LIKE '%mart%'
      → Encuentra 'Martillo', 'Martillo 16oz', etc.
      Los % significan "cualquier texto en esa posición".
    """
    mostrar_titulo("BUSCAR PRODUCTO")
    termino = input("  Escribe nombre o código a buscar: ").strip()

    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.codigo, p.nombre,
               COALESCE(c.nombre, 'Sin cat.') AS categoria,
               p.precio_venta, p.stock
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.nombre LIKE ? OR p.codigo LIKE ?
        ORDER BY p.nombre
    """, (f"%{termino}%", f"%{termino}%"))
    resultados = cursor.fetchall()
    conn.close()

    if resultados:
        print()
        print(tabulate(resultados,
                       headers=["Código", "Nombre", "Categoría", "P.Venta", "Stock"],
                       tablefmt="rounded_outline"))
        print(f"\n  Se encontraron {len(resultados)} resultado(s).")
    else:
        mensaje_alerta(f"No se encontraron productos con '{termino}'.")


def editar_precio_producto():
    """
    Cambia el precio de compra y/o venta de un producto.

    SQL UPDATE:
      UPDATE productos SET precio_compra = ? WHERE codigo = ?
      → Modifica solo la fila con ese código.
      → Si el usuario dejó el campo vacío, no actualiza ese precio.
    """
    mostrar_titulo("EDITAR PRECIO DE PRODUCTO")
    codigo = input("  Código del producto: ").strip().upper()

    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nombre, precio_compra, precio_venta FROM productos WHERE codigo = ?",
        (codigo,)
    )
    producto = cursor.fetchone()  # fetchone() = solo el primer resultado

    if not producto:
        conn.close()
        mensaje_error(f"No existe ningún producto con el código '{codigo}'.")
        return

    print(f"\n  Producto:             {producto[0]}")
    print(f"  Precio compra actual: Q {producto[1]:,.2f}")
    print(f"  Precio venta actual:  Q {producto[2]:,.2f}")
    print("\n  (Presiona Enter para no cambiar ese precio)\n")

    try:
        nuevo_compra = input("  Nuevo precio de compra (Q): ").strip()
        nuevo_venta  = input("  Nuevo precio de venta  (Q): ").strip()

        if nuevo_compra:
            cursor.execute("UPDATE productos SET precio_compra = ? WHERE codigo = ?",
                           (float(nuevo_compra), codigo))
        if nuevo_venta:
            cursor.execute("UPDATE productos SET precio_venta = ? WHERE codigo = ?",
                           (float(nuevo_venta), codigo))

        conn.commit()
        conn.close()
        mensaje_exito("Precio(s) actualizados correctamente.")

    except ValueError:
        mensaje_error("El precio debe ser un número (ej: 25.50).")


def agregar_stock_producto():
    """
    Suma unidades al stock de un producto cuando llega mercancía nueva.

    SQL UPDATE con suma:
      UPDATE productos SET stock = stock + ? WHERE id = ?
      → stock = stock + cantidad_nueva
      → NO reemplaza el stock, lo INCREMENTA.
    """
    mostrar_titulo("AGREGAR STOCK — INGRESO DE MERCANCÍA")
    codigo = input("  Código del producto: ").strip().upper()

    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, stock FROM productos WHERE codigo = ?", (codigo,))
    producto = cursor.fetchone()

    if not producto:
        conn.close()
        mensaje_error(f"No existe ningún producto con el código '{codigo}'.")
        return

    print(f"\n  Producto:     {producto[1]}")
    print(f"  Stock actual: {producto[2]} unidades")

    try:
        cantidad = int(input("\n  ¿Cuántas unidades ingresar? "))
        if cantidad <= 0:
            mensaje_error("La cantidad debe ser mayor a cero.")
            conn.close()
            return

        cursor.execute("UPDATE productos SET stock = stock + ? WHERE id = ?",
                       (cantidad, producto[0]))
        conn.commit()
        conn.close()

        nuevo_stock = producto[2] + cantidad
        mensaje_exito(f"Stock actualizado. Nuevo stock: {nuevo_stock} unidades.")

    except ValueError:
        mensaje_error("La cantidad debe ser un número entero (ej: 10).")


# ═════════════════════════════════════════════════════════════════
#  MÓDULO 3 — INVENTARIO
#  El inventario es la "fotografía actual" del stock:
#  cuántos productos hay, cuáles están bajos, cuánto valen.
# ═════════════════════════════════════════════════════════════════

def menu_inventario():
    """Submenú del módulo de inventario con tres vistas."""
    while True:
        limpiar_pantalla()
        mostrar_titulo("MÓDULO 3 → INVENTARIO")
        print("  [1] Ver inventario completo (por categoría)")
        print("  [2] Ver alertas de stock bajo")
        print("  [3] Ver valor total del inventario")
        print("  [0] Volver al menú principal")

        opcion = input(f"\n{Fore.CYAN}  Elige una opción: {Style.RESET_ALL}").strip()

        if opcion == "1":
            inventario_completo()
        elif opcion == "2":
            alertas_stock_bajo()
        elif opcion == "3":
            valor_inventario()
        elif opcion == "0":
            break
        else:
            mensaje_error("Opción no válida.")
        pausar()


def inventario_completo():
    """
    Muestra todos los productos ordenados por categoría.

    ORDER BY c.nombre, p.nombre
    → Primero ordena por categoría, luego por nombre dentro de cada categoría.
    → Ej: todos los de Herramientas juntos, luego todos los de Plomería...
    """
    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(c.nombre, 'Sin categoría') AS categoria,
               p.codigo, p.nombre, p.stock, p.stock_minimo, p.precio_venta
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        ORDER BY c.nombre, p.nombre
    """)
    filas = cursor.fetchall()
    conn.close()

    mostrar_titulo("INVENTARIO COMPLETO")
    if filas:
        tabla = []
        for f in filas:
            bajo   = f[3] <= f[4]
            estado = f"{Fore.RED}⚠ REABASTECER{Style.RESET_ALL}" if bajo else f"{Fore.GREEN}✔ OK{Style.RESET_ALL}"
            tabla.append([f[0], f[1], f[2], f[3], f[4], f"Q {f[5]:,.2f}", estado])

        print(tabulate(tabla,
                       headers=["Categoría", "Código", "Producto",
                                 "Stock", "Mín.", "P.Venta", "Estado"],
                       tablefmt="rounded_outline"))

        total   = len(filas)
        alertas = sum(1 for f in filas if f[3] <= f[4])
        print(f"\n  Total productos: {Fore.CYAN}{total}{Style.RESET_ALL}  |  "
              f"En alerta: {Fore.RED}{alertas}{Style.RESET_ALL}")
    else:
        mensaje_alerta("No hay productos en el inventario.")


def alertas_stock_bajo():
    """
    Muestra SOLO los productos con stock ≤ stock_mínimo.

    SQL:
      WHERE p.stock <= p.stock_minimo
      → Compara dos columnas del mismo registro.
      ORDER BY p.stock ASC
      → Los más urgentes (menor stock) aparecen primero.
    """
    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.codigo, p.nombre,
               COALESCE(c.nombre, 'Sin cat.') AS categoria,
               p.stock, p.stock_minimo
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.stock <= p.stock_minimo
        ORDER BY p.stock ASC
    """)
    filas = cursor.fetchall()
    conn.close()

    mostrar_titulo("⚠  ALERTAS DE STOCK BAJO")
    if filas:
        tabla = []
        for f in filas:
            if f[3] == 0:
                estado = f"{Fore.RED}🔴 AGOTADO{Style.RESET_ALL}"
            else:
                estado = f"{Fore.YELLOW}🟡 BAJO{Style.RESET_ALL}"
            tabla.append([f[0], f[1], f[2], f[3], f[4], estado])

        print(tabulate(tabla,
                       headers=["Código", "Producto", "Categoría",
                                 "Stock", "Mínimo", "Estado"],
                       tablefmt="rounded_outline"))
        print(f"\n  {Fore.RED}{len(filas)} producto(s) requieren reposición.{Style.RESET_ALL}")
    else:
        mensaje_exito("¡Todo el inventario está en niveles adecuados!")


def valor_inventario():
    """
    Calcula el valor económico del inventario por categoría.

    FÓRMULAS:
      Valor costo   = SUM(stock × precio_compra) → capital invertido
      Valor venta   = SUM(stock × precio_venta)  → valor si se vende todo
      Ganancia pot. = valor venta - valor costo  → ganancia máxima posible

    SQL:
      GROUP BY c.nombre → hace los cálculos por cada categoría por separado
      SUM(p.stock * p.precio_compra) → multiplicación dentro de SQL
    """
    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(c.nombre, 'Sin categoría'),
               COALESCE(SUM(p.stock * p.precio_compra), 0),
               COALESCE(SUM(p.stock * p.precio_venta),  0)
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        GROUP BY c.nombre
        ORDER BY c.nombre
    """)
    filas = cursor.fetchall()
    conn.close()

    mostrar_titulo("VALOR DEL INVENTARIO POR CATEGORÍA")
    if filas:
        tabla       = []
        total_costo = 0.0
        total_venta = 0.0

        for f in filas:
            costo    = f[1]
            venta    = f[2]
            ganancia = venta - costo
            total_costo += costo
            total_venta += venta
            tabla.append([f[0], f"Q {costo:,.2f}", f"Q {venta:,.2f}", f"Q {ganancia:,.2f}"])

        print(tabulate(tabla,
                       headers=["Categoría", "Valor Costo", "Valor Venta", "Ganancia Pot."],
                       tablefmt="rounded_outline"))

        print(f"\n  {'─' * 53}")
        print(f"  {'TOTAL INVERTIDO (costo):':40} Q {total_costo:,.2f}")
        print(f"  {'TOTAL VALOR DE VENTA:':40} Q {total_venta:,.2f}")
        print(f"  {Fore.GREEN}{'GANANCIA POTENCIAL TOTAL:':40} Q {total_venta - total_costo:,.2f}{Style.RESET_ALL}")
    else:
        mensaje_alerta("No hay datos de inventario disponibles.")


# ═════════════════════════════════════════════════════════════════
#  MÓDULO 5 — REPORTES
#  Convierten los datos en información útil para tomar decisiones.
# ═════════════════════════════════════════════════════════════════

def menu_reportes():
    """Submenú del módulo de reportes con cinco análisis."""
    while True:
        limpiar_pantalla()
        mostrar_titulo("MÓDULO 5 → REPORTES")
        print("  [1] Resumen general del negocio")
        print("  [2] Productos por categoría")
        print("  [3] Valor del inventario por categoría")
        print("  [4] Productos con mayor margen de ganancia")
        print("  [5] Productos críticos (stock bajo / agotado)")
        print("  [0] Volver al menú principal")

        opcion = input(f"\n{Fore.CYAN}  Elige una opción: {Style.RESET_ALL}").strip()

        if opcion == "1":
            reporte_resumen_general()
        elif opcion == "2":
            reporte_productos_por_categoria()
        elif opcion == "3":
            reporte_valor_por_categoria()
        elif opcion == "4":
            reporte_mayor_margen()
        elif opcion == "5":
            reporte_productos_criticos()
        elif opcion == "0":
            break
        else:
            mensaje_error("Opción no válida.")
        pausar()


def reporte_resumen_general():
    """
    Tablero de control: los números más importantes del negocio de un vistazo.
    Hace varias consultas SQL pequeñas y las presenta juntas.
    """
    conn   = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM productos")
    total_productos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM categorias")
    total_categorias = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo")
    stock_bajo = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM productos WHERE stock = 0")
    agotados = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(stock * precio_compra), 0) FROM productos")
    capital_invertido = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(stock * precio_venta), 0) FROM productos")
    valor_venta_total = cursor.fetchone()[0]

    conn.close()

    ganancia_potencial = valor_venta_total - capital_invertido

    mostrar_titulo("📊  RESUMEN GENERAL DEL NEGOCIO")
    print(f"  {'─' * 50}")
    print(f"  {'Productos en catálogo:':35} {Fore.CYAN}{total_productos}{Style.RESET_ALL}")
    print(f"  {'Categorías registradas:':35} {Fore.CYAN}{total_categorias}{Style.RESET_ALL}")
    print(f"  {'─' * 50}")
    print(f"  {'Productos con stock bajo:':35} {Fore.YELLOW}{stock_bajo}{Style.RESET_ALL}")
    print(f"  {'Productos agotados:':35} {Fore.RED}{agotados}{Style.RESET_ALL}")
    print(f"  {'─' * 50}")
    print(f"  {'Capital invertido:':35} Q {capital_invertido:,.2f}")
    print(f"  {'Valor total de venta:':35} Q {valor_venta_total:,.2f}")
    print(f"  {Fore.GREEN}{'Ganancia potencial:':35} Q {ganancia_potencial:,.2f}{Style.RESET_ALL}")
    print(f"  {'─' * 50}")


def reporte_productos_por_categoria():
    """
    Cuántos productos y cuánto stock acumula cada categoría.

    SQL:
      COUNT(p.id)       → cuenta cuántos productos hay en esa categoría
      SUM(p.stock)      → suma el stock de todos los productos del grupo
      AVG(p.precio_venta) → precio promedio de venta en esa categoría
      ORDER BY COUNT DESC → las categorías con más productos primero
    """
    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(c.nombre, 'Sin categoría'),
               COUNT(p.id)               AS num_productos,
               COALESCE(SUM(p.stock), 0) AS stock_total,
               COALESCE(AVG(p.precio_venta), 0) AS precio_promedio
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        GROUP BY c.nombre
        ORDER BY COUNT(p.id) DESC
    """)
    filas = cursor.fetchall()
    conn.close()

    mostrar_titulo("PRODUCTOS POR CATEGORÍA")
    if filas:
        tabla = [[f[0], f[1], f[2], f"Q {f[3]:,.2f}"] for f in filas]
        print(tabulate(tabla,
                       headers=["Categoría", "Nº Productos", "Stock Total", "P.Venta Prom."],
                       tablefmt="rounded_outline"))
    else:
        mensaje_alerta("No hay datos para este reporte.")


def reporte_valor_por_categoria():
    """
    Cuánto capital hay en cada categoría y su porcentaje del total.

    Porcentaje:
      % = (valor_venta_categoria / valor_venta_total) × 100

    Útil para saber en qué línea de productos conviene invertir más.
    """
    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(c.nombre, 'Sin categoría'),
               COALESCE(SUM(p.stock * p.precio_compra), 0),
               COALESCE(SUM(p.stock * p.precio_venta),  0)
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        GROUP BY c.nombre
        ORDER BY SUM(p.stock * p.precio_venta) DESC
    """)
    filas = cursor.fetchall()
    conn.close()

    mostrar_titulo("VALOR DEL INVENTARIO POR CATEGORÍA")
    if filas:
        total_venta = sum(f[2] for f in filas) or 1  # Evitar división por cero

        tabla = []
        for f in filas:
            costo = f[1];  venta = f[2]
            pct   = (venta / total_venta) * 100
            tabla.append([f[0], f"Q {costo:,.2f}", f"Q {venta:,.2f}",
                          f"Q {venta-costo:,.2f}", f"{pct:.1f}%"])

        print(tabulate(tabla,
                       headers=["Categoría", "Valor Costo", "Valor Venta",
                                 "Ganancia Pot.", "% del Total"],
                       tablefmt="rounded_outline"))
    else:
        mensaje_alerta("No hay datos para este reporte.")


def reporte_mayor_margen():
    """
    Lista productos ordenados por margen de ganancia de mayor a menor.

    MARGEN DE GANANCIA:
      ganancia_unitaria = precio_venta - precio_compra
      margen_%          = (ganancia / precio_compra) × 100

    Ejemplo:
      Martillo: compra Q 50, venta Q 80 → ganancia Q 30 → margen 60%

    Los productos con mayor margen son los más rentables.
    ORDER BY ganancia_unitaria DESC → los más rentables primero.
    """
    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.codigo, p.nombre,
               COALESCE(c.nombre, 'Sin cat.') AS categoria,
               p.precio_compra, p.precio_venta,
               (p.precio_venta - p.precio_compra) AS ganancia_unitaria
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.precio_compra > 0
        ORDER BY ganancia_unitaria DESC
    """)
    filas = cursor.fetchall()
    conn.close()

    mostrar_titulo("PRODUCTOS CON MAYOR MARGEN DE GANANCIA")
    if filas:
        tabla = []
        for f in filas:
            margen_pct = (f[5] / f[3]) * 100 if f[3] > 0 else 0
            tabla.append([f[0], f[1], f[2],
                          f"Q {f[3]:,.2f}", f"Q {f[4]:,.2f}",
                          f"Q {f[5]:,.2f}", f"{margen_pct:.1f}%"])

        print(tabulate(tabla,
                       headers=["Código", "Producto", "Categoría",
                                 "P.Compra", "P.Venta", "Ganancia/u", "Margen %"],
                       tablefmt="rounded_outline"))
    else:
        mensaje_alerta("No hay productos con precio de compra registrado.")


def reporte_productos_criticos():
    """
    Lista los productos con stock bajo o agotado, con el déficit calculado.

    DÉFICIT = stock_minimo - stock_actual
    → Cuántas unidades faltan para llegar al mínimo.
    → Es tu "lista de compras urgente".

    SQL:
      (p.stock_minimo - p.stock) AS deficit
      → Resta directamente en la consulta SQL.
    """
    conn   = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.codigo, p.nombre,
               COALESCE(c.nombre, 'Sin cat.') AS categoria,
               p.stock, p.stock_minimo,
               (p.stock_minimo - p.stock) AS deficit
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.stock <= p.stock_minimo
        ORDER BY p.stock ASC, p.nombre ASC
    """)
    filas = cursor.fetchall()
    conn.close()

    mostrar_titulo("⚠  PRODUCTOS CRÍTICOS — LISTA DE REPOSICIÓN")
    if filas:
        tabla = []
        for f in filas:
            estado = f"{Fore.RED}🔴 AGOTADO{Style.RESET_ALL}" if f[3] == 0 else f"{Fore.YELLOW}🟡 BAJO{Style.RESET_ALL}"
            tabla.append([f[0], f[1], f[2], f[3], f[4], f[5], estado])

        print(tabulate(tabla,
                       headers=["Código", "Producto", "Categoría",
                                 "Stock", "Mínimo", "Déficit", "Estado"],
                       tablefmt="rounded_outline"))

        agotados = sum(1 for f in filas if f[3] == 0)
        bajos    = len(filas) - agotados
        print(f"\n  Agotados: {Fore.RED}{agotados}{Style.RESET_ALL}  |  "
              f"Bajos: {Fore.YELLOW}{bajos}{Style.RESET_ALL}  |  "
              f"Total urgente: {Fore.RED}{len(filas)}{Style.RESET_ALL}")
    else:
        mensaje_exito("¡Todo el inventario está en niveles adecuados!")


# ─────────────────────────────────────────────────────────────────
# MENÚ PRINCIPAL
# ─────────────────────────────────────────────────────────────────

def menu_principal():
    """
    Puerta de entrada al sistema. Bucle infinito que muestra opciones
    hasta que el usuario elige salir con la opción 0.
    """
    while True:
        limpiar_pantalla()
        print(f"\n{Fore.CYAN}  ╔══════════════════════════════════════════════╗")
        print(f"  ║    🔧  FERRETERÍA — SISTEMA DE GESTIÓN        ║")
        print(f"  ╚══════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        print(f"  {Fore.YELLOW}[1]{Style.RESET_ALL} 📦  Módulo 1  — Productos")
        print(f"  {Fore.YELLOW}[2]{Style.RESET_ALL} ⚙   Módulo 1  — Categorías")
        print(f"  {Fore.YELLOW}[3]{Style.RESET_ALL} 🗂   Módulo 3  — Inventario")
        print(f"  {Fore.YELLOW}[4]{Style.RESET_ALL} 📊  Módulo 5  — Reportes")
        print(f"  {Fore.RED}[0]{Style.RESET_ALL} ❌  Salir")

        opcion = input(f"\n{Fore.CYAN}  Selecciona un módulo: {Style.RESET_ALL}").strip()

        if opcion == "1":
            menu_productos()
        elif opcion == "2":
            menu_categorias()
        elif opcion == "3":
            menu_inventario()
        elif opcion == "4":
            menu_reportes()
        elif opcion == "0":
            limpiar_pantalla()
            print(f"\n  {Fore.GREEN}Sistema cerrado. ¡Hasta pronto!{Style.RESET_ALL}\n")
            break
        else:
            mensaje_error("Opción no válida. Elige entre 0 y 4.")
            pausar()


# ─────────────────────────────────────────────────────────────────
# PUNTO DE ARRANQUE
# ─────────────────────────────────────────────────────────────────
# if __name__ == "__main__" solo se ejecuta cuando corres:
#   python ferreteria.py
# No se ejecuta si otro archivo importa este módulo.

if __name__ == "__main__":
    crear_tablas()    # 1. Preparar la base de datos
    menu_principal()  # 2. Lanzar el programa