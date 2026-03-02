# 🔧 Ferretería — Sistema de Gestión

> Sistema de escritorio para gestionar productos, inventario y ventas de una ferretería.  
> Disponible en **dos interfaces gráficas**: Tkinter (incluida en Python) y PyQt6 (moderna y estilizada).

---

## 📸 Módulos del sistema

| Módulo | Ícono | Acceso | Descripción |
|--------|-------|--------|-------------|
| Productos | 📦 | Admin | Registrar, buscar y editar precios del catálogo |
| Categorías | ⚙ | Admin | Organizar productos por familia o tipo |
| Inventario | 🗂 | Admin / Vendedor | Ver stock, alertas de reposición y valor total |
| Ventas | 🧾 | Admin / Vendedor | Carrito de compra, confirmar venta, historial |
| Reportes | 📊 | Admin | KPIs, productos críticos, valor por categoría |
| Usuarios | 👤 | Admin | Crear, activar/desactivar y cambiar contraseñas |

---

## 🔐 Roles de usuario

```
admin     →  Acceso completo a todos los módulos
vendedor  →  Solo Ventas + Inventario (lectura)
```

Las contraseñas se almacenan cifradas con **SHA-256**.  
Cuentas por defecto al iniciar por primera vez:

```
usuario: admin      contraseña: admin123
usuario: vendedor   contraseña: vend123
```

---

## 🖥️ Interfaces gráficas

### Versión Tkinter — `ferreteria_gui.py`
- Usa la librería **Tkinter**, que viene **incluida con Python** — no requiere instalación extra
- Tema naranja y gris oscuro
- Sidebar colapsable con botón ☰ / ✕
- Ventana adaptable al DPI y tamaño de fuente del sistema

### Versión PyQt6 — `ferreteria_qt.py`
- Usa **PyQt6**, interfaz más moderna con estilo Fusion
- Splitter redimensionable en el módulo de ventas
- Misma funcionalidad que la versión Tkinter
- Requiere instalación (ver dependencias)

---

## ⚙️ Tecnologías utilizadas

| Tecnología | Versión recomendada | Uso |
|------------|-------------------|-----|
| Python | 3.10 o superior | Lenguaje principal |
| Tkinter | Incluida en Python | Interfaz versión GUI clásica |
| PyQt6 | 6.x | Interfaz versión GUI moderna |
| SQLite3 | Incluida en Python | Base de datos local |
| hashlib | Incluida en Python | Cifrado SHA-256 de contraseñas |
| datetime | Incluida en Python | Fechas y horas en ventas |

---

## 📦 Dependencias a instalar

### Para la versión Tkinter (`ferreteria_gui.py`)

En **Windows y macOS** Tkinter ya viene instalado con Python.  
En **Linux** puede ser necesario instalarlo:

```bash
# Ubuntu / Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

Verifica que funcione:
```bash
python3 -c "import tkinter; print('Tkinter OK ✔')"
```

---

### Para la versión PyQt6 (`ferreteria_qt.py`)

```bash
pip install PyQt6
```

Verifica que funcione:
```bash
python3 -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK ✔')"
```

---

## 🚀 Cómo ejecutar

```bash
# Versión Tkinter
python ferreteria_gui.py

# Versión PyQt6
python ferreteria_qt.py
```

Ambas versiones **comparten la misma base de datos** `ferreteria.db`.  
Si el archivo no existe, se crea automáticamente al iniciar el programa.

---

## 📁 Estructura del proyecto

```
ferreteria/
│
├── ferreteria_gui.py        # Interfaz Tkinter (no requiere instalación)
├── ferreteria_qt.py         # Interfaz PyQt6   (requiere pip install PyQt6)
├── ferreteria.db            # Base de datos SQLite (se genera automáticamente)
└── README.md                # Este archivo
```

---

## 🗂️ Estructura de la base de datos

```
usuarios          → Cuentas de acceso con rol y contraseña cifrada
categorias        → Familias de productos (ej: Plomería, Eléctrico)
productos         → Catálogo con precios, stock y categoría
ventas            → Cabecera de cada venta (número, cliente, fecha, total)
detalle_ventas    → Ítems individuales de cada venta
```

---

## ✅ Compatibilidad

| Sistema Operativo | Tkinter | PyQt6 |
|-------------------|---------|-------|
| Windows 10 / 11   | ✔       | ✔     |
| Ubuntu / Debian   | ✔ *     | ✔     |
| Fedora / Arch     | ✔ *     | ✔     |
| macOS             | ✔       | ✔     |

`*` Requiere instalar `python3-tk` desde el gestor de paquetes del sistema.

---

## 🛠️ Hecho con

- **Python 3** — lógica del negocio y acceso a datos
- **Tkinter** — interfaz gráfica nativa, sin dependencias externas
- **PyQt6** — interfaz gráfica moderna con Qt Framework
- **SQLite** — base de datos embebida, sin servidor

---

*Proyecto académico — Sistema de gestión para ferretería pequeña o mediana.*
