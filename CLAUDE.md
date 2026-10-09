# CLAUDE.md

Contexto del proyecto para Claude Code. Léelo completo antes de proponer o aplicar
cambios.

## Qué es este proyecto

Aplicación de consola en Python para administrar el inventario y las ventas de una
tienda pequeña ("La Esquina"). Es el **reto de refactorización asistida por IA**: el
programa funciona y todas las pruebas pasan, pero el código tiene muchas malas
prácticas. El objetivo es **mejorar la calidad del código sin cambiar su
comportamiento observable**.

## Qué debe hacer el programa (reglas de negocio)

Estas reglas son el comportamiento que hay que conservar en cualquier refactorización:

- **Alta de productos** (`agregarProducto(codigo, nombre, precio, stock)`): rechaza
  código vacío o `None`, código duplicado, `precio <= 0` y `stock < 0`. Cada producto
  es un `dict` con las llaves `codigo`, `nombre`, `precio`, `stock`.
- **Eliminar producto** y **actualizar stock** (suma o resta). El stock nunca puede
  quedar negativo.
- **Búsqueda** (`buscarProducto(texto)`): por subcadena del nombre, sin importar
  mayúsculas; regresa una lista de productos.
- **Registrar venta** (`registrar_venta(codigo, cantidad, cliente="")`):
  1. Valida en este orden: código vacío → producto inexistente → cantidad inválida
     (`None` o `<= 0`) → stock insuficiente. Si falla, regresa `None`, no modifica nada
     y deja el motivo en `gestor.ultimo_error`.
  2. `subtotal = precio * cantidad`.
  3. Descuento por volumen: **10 %** si subtotal `>= 1000`; **5 %** si `>= 500`; si no,
     0.
  4. Descuento extra **VIP**: si el cliente empieza con `"VIP"` y
     `subtotal - descuento > 200`, se suma un **2 % del subtotal** al descuento.
  5. `IVA = 16 %` sobre `subtotal - descuento`; `total = round(base + IVA, 2)`.
  6. Descuenta el stock, incrementa el folio (`contador_ventas`) y guarda la venta en
     `VENTAS` con: `folio, codigo, nombre, cantidad, subtotal, descuento, impuesto,
     total, cliente, fecha, ticket`.
  7. El `ticket` es un texto plano con encabezado `TIENDA LA ESQUINA`; la línea de
     descuento solo aparece si el descuento es mayor que 0.
- **Cotizar** (`cotizar(codigo, cantidad)`): calcula el total con descuento por
  volumen e IVA **sin** registrar la venta. No aplica VIP ni revisa stock. Debe
  coincidir con el total de la venta equivalente sin cliente.
- **Reportes**: stock bajo (`stock < 5`), reporte de inventario (marca
  `<-- STOCK BAJO` e incluye el valor total), total vendido, los más vendidos
  (`mas_vendidos(n=3)` → lista de tuplas `(codigo, unidades)` en orden descendente) y
  resumen de ventas. `reporte_inventario` y `resumen_ventas` imprimen el texto **y**
  lo regresan.
- **Persistencia** en JSON (`guardar_datos` / `cargar_datos`): guarda inventario,
  ventas y contador; al recargar, el folio continúa. `cargar_datos` regresa `False` si
  el archivo no existe o está corrupto.

## Estructura

```
src/
  gestor.py    # Estado global + lógica de productos y ventas (el núcleo)
  almacen.py   # Carga/guardado en JSON; escribe directamente en el estado de gestor
  reportes.py  # Reportes e indicadores; lee gestor.INVENTARIO y gestor.VENTAS
  main.py      # Menú interactivo (input/print); usa datos_ejemplo.json relativo al cwd
tests/         # Pruebas pytest de caja negra (NO se modifican)
docs/
  bitacora.md  # Bitácora de refactorizaciones (prompt, cambio, justificación, tests)
  reflexion.md # Reflexión final sobre el trabajo con la IA
datos_ejemplo.json   # Datos semilla para el menú interactivo
pyproject.toml       # Configuración de ruff y pytest (NO se modifica)
BITACORA_TEMPLATE.md # Plantilla de la bitácora de prompts
```

Los módulos se importan como módulos sueltos (`import gestor`), no como paquete:
`tests/conftest.py` agrega `src/` al `sys.path` y `main.py` se ejecuta desde `src/`.

### Estado global

`gestor.py` guarda el estado en variables de módulo: `INVENTARIO` (dict
código → producto), `VENTAS` (lista), `contador_ventas` (último folio) y `ultimo_error`
(texto del último error). `almacen.py` y `reportes.py` las leen y modifican
directamente.

## API pública que usan los tests (no romper)

Los tests llaman o leen estos nombres. Hay que conservar sus nombres, firmas, tipos de
retorno y la forma de los diccionarios:

- `gestor`: `INVENTARIO`, `VENTAS`, `reiniciar_sistema()`, `agregarProducto()`,
  `eliminar_producto()`, `actualizar_stock()`, `buscarProducto()`,
  `registrar_venta()`, `cotizar()`.
- `almacen`: `guardar_datos(ruta)` (regresa `True`), `cargar_datos(ruta)`.
- `reportes`: `productos_stock_bajo()`, `total_vendido()`, `mas_vendidos(n)`,
  `reporte_inventario()`.

`agregarProducto` y `buscarProducto` **conservan su nombre en camelCase** (están
exentos en `pyproject.toml`). `INVENTARIO` y `VENTAS` se acceden siempre como
`gestor.INVENTARIO` / `gestor.VENTAS`; se vacían con `.clear()` en lugar de
reasignarse, y conviene mantenerlo así para que ninguna referencia quede apuntando a un
objeto viejo. `contador_ventas` (antes `contadorVentas`), `ultimo_error`,
`hay_archivo` (antes `hayArchivo`) y `formatear_dinero` (antes `hacer_cosa`) no los
usan los tests, pero sí otros módulos: si se renombran, hay que actualizar todas sus
referencias.

## Comandos

En Windows (PowerShell), desde la raíz del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

pytest                 # deben pasar las 20 pruebas
ruff check src         # objetivo final: 0 errores
cd src; python main.py # app interactiva (opcional)
```

Si el entorno no está activado, usar `.venv\Scripts\python -m pytest` y
`.venv\Scripts\python -m ruff check src`.

Estado inicial: **20/20 pruebas pasan** y **ruff reporta 20 errores** (UP009, SIM102,
SIM115, C901, N802, SIM108, N816, SIM103, UP015, I001, F401).

## Reglas obligatorias

1. **No modificar nada en `tests/`** (ni `conftest.py`). Si una prueba falla después de
   un cambio, el error está en el cambio y se corrige en `src/`, nunca en el test.
2. **No modificar `pyproject.toml`** para silenciar el linter (no agregar `ignore`,
   `noqa` generalizados ni subir `max-complexity`).
3. **El comportamiento observable debe quedar idéntico**: valores de retorno, mensajes
   de `ultimo_error`, cálculos y redondeos, formato del ticket y de los reportes, texto
   del menú y formato del JSON guardado.
4. **Una refactorización a la vez.** Después de **cada** cambio ejecutar `pytest` y
   `ruff check src` y mostrar el resultado antes de seguir.
5. Cambios **pequeños y revisables**: un commit atómico por refactorización. Explica
   qué cambia y por qué antes de aplicarlo.
6. Solo Python estándar (3.10+). No agregar dependencias.
7. No leer ni editar entornos virtuales, cachés ni datos generados (ver
   `.claudeignore`).

## Code smells conocidos (punto de partida)

- `registrar_venta`: función gigante (C901) que valida, calcula, descuenta stock, arma
  el ticket y guarda; tiene `if` anidados en pirámide.
- Cálculo de descuento + IVA **duplicado** entre `registrar_venta` y `cotizar`.
- **Números mágicos**: 1000, 500, 0.10, 0.05, 0.02, 200, 0.16, el prefijo `"VIP"` y el
  mínimo de stock 5 (repetido en dos funciones de `reportes.py`).
- **Nombres crípticos**: `x`, `aux`, `temp2`, `t`, `d`, `desc`, `hacer_cosa`; mezcla de
  camelCase y snake_case (`contadorVentas`, `hayArchivo`, `reporteViejoCSV`).
- **Código muerto**: `calcular_descuento_viejo`, `reporteViejoCSV`, el bloque
  comentado `exportar_txt`, `MODO_DEBUG` y el `import os` sin usar en `reportes.py`.
- Archivos abiertos sin `with` (SIM115) y `except Exception` demasiado amplio en
  `almacen.py`.
- Burbuja manual en `mas_vendidos` (se puede usar `sorted`, cuidando que sea estable
  para empatar igual).
- `menu()` en `main.py` mezcla entrada/salida con la lógica (C901).
- Declaraciones `# -*- coding: utf-8 -*-` innecesarias en Python 3 (UP009).

## Flujo de entrega

- Trabajar en la rama `refactorizacion` y entregar con un PR hacia `main`.
- Documentar cada refactorización en `docs/bitacora.md` (copia de `BITACORA_TEMPLATE.md`):
  prompt usado, cambio realizado, justificación y resultado de los tests.
- Escribir en español los mensajes de commit, comentarios y docstrings, igual que en el
  resto del código.
