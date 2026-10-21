# Ferretería — Sistema de gestión de inventario y ventas

Aplicación de escritorio en **Python + Tkinter + SQLite** para gestionar los productos, el inventario y las ventas de una ferretería pequeña o mediana. Incluye además una versión de consola con los módulos de productos, categorías, inventario y reportes.

## Funcionalidades

Versión de escritorio (`ferreteria_gui.py`), organizada en 5 módulos con una barra lateral:

| Módulo | Qué hace |
|---|---|
| Productos | Registra productos con código único, los busca, edita precios de compra y venta, y agrega stock |
| Categorías | Crea y lista las familias de productos (por ejemplo, Plomería o Eléctrico) |
| Inventario | Muestra el inventario completo, las alertas de productos en su stock mínimo o por debajo, y el valor del inventario |
| Ventas | Carrito de compra con validación de stock, confirmación de la venta con número correlativo (V-00001, V-00002…) e historial con el detalle de cada venta |
| Reportes | Resumen con indicadores del negocio, productos por categoría, valor por categoría y productos críticos que hay que reponer |

El resumen de reportes muestra el total de productos y categorías, cuántos productos están en alerta o sin stock, y el valor del inventario a precio de costo y a precio de venta.

## Decisiones técnicas

- **La venta es una transacción.** Al confirmar se generan el número de venta, la cabecera, el detalle y el descuento de stock de cada producto; si algo falla se hace `rollback` y el inventario queda como estaba.
- **El carrito valida el stock antes de agregar.** Cuenta también las unidades de ese producto que ya están en el carrito, para no vender más de lo que hay en bodega.
- **Interfaz adaptable a la pantalla.** Al iniciar se calcula un factor de escala a partir del DPI del monitor, y fuentes, márgenes y botones crecen con él. La barra lateral se puede colapsar.
- **La base de datos se crea sola.** Las tablas se crean con `CREATE TABLE IF NOT EXISTS` al iniciar, así que no hace falta ningún script de instalación.

## Requisitos

- Python 3.10 o superior.
- Tkinter y SQLite vienen incluidos con Python en Windows y macOS. En Linux puede que haya que instalar Tkinter:

```bash
sudo apt install python3-tk
```

(En Fedora es `python3-tkinter` y en Arch, `tk`.)

- La versión de consola usa dos librerías externas:

```bash
pip install tabulate colorama
```

## Cómo ejecutarlo

```bash
python ferreteria_gui.py   # versión de escritorio
python main.py             # versión de consola
```

Las dos versiones usan el mismo archivo `ferreteria.db` en la carpeta desde donde se ejecutan. Si no existe, se crea al iniciar.

## Estructura

```
├── ferreteria_gui.py   # versión de escritorio (Tkinter): los 5 módulos
├── main.py             # versión de consola: productos, categorías, inventario y reportes
├── ferreteria.db       # base de datos SQLite (se crea al iniciar si no existe)
└── README.md
```

## Base de datos

```
categorias       → familias de productos
productos        → código, nombre, precios de compra y venta, stock, stock mínimo y categoría
ventas           → número, cliente, fecha, total y estado de cada venta
detalle_ventas   → productos, cantidades y subtotales de cada venta
```

## Autor

**John Neider Cuervo Quintero** — estudiante de Ingeniería de Software y Datos, Medellín.
Portafolio: [portafolio-john-cuervo.netlify.app](https://portafolio-john-cuervo.netlify.app/)
