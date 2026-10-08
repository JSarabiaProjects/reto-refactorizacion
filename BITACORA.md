# Bitácora de refactorización

**Nombre:**
**Matrícula:**
**Fecha:** 2026-10-08

Registra aquí **cada refactorización** que realices con Claude Code. Copia el
prompt tal cual lo escribiste (o un resumen fiel si fue una conversación larga),
describe el cambio que se aplicó al código y justifica por qué mejora la calidad.
Después de cada cambio ejecuta `pytest` y anota el resultado.

## Preparación

Antes de refactorizar se configuró el proyecto y se pidió un diagnóstico. Estos
pasos no modificaron `src/`.

| Paso | Prompt usado | Resultado |
|------|--------------|-----------|
| Configuración | "Inicializemos el CLAUDE.md. Define lo que en teoria deberia de hacer el proyecto, haz un pequeño analisis del repositorio, para que el archivo contenga todo el contexto del proyecto, al igual define que no tocaremos los test, no deben ser modificados. Genera el .claudeignore, agregando (entornos virtuales, cachés, datos generados) ya que no se deben leer, y realiza un comentario en nuestro repositorio si lo consideras necesario indicando que se realizo en esta inicializacion." | `CLAUDE.md` con las reglas de negocio, la API pública que usan los tests, los comandos y las reglas obligatorias (no modificar `tests/` ni `pyproject.toml`, comportamiento idéntico, una refactorización a la vez). `.claudeignore` excluye `.venv/` (también `src/.venv`), cachés y el JSON generado en `src/`. Commit `31c2dd5`. |
| Diagnóstico | "Ahora analicemos el codigo src, necesitamos diagnosticar posibles areas de oportunidad en el codigo escrito que es muy basico, requerimos detectar posibles refactorizaciones para que podamos aplicarlas posteriormente. Tales como la legibilidad y mantenibilidad. La escalabilidad, aunque ahora es proyecto pequeño, pero define mejoras para que sea escalable. Analza rendimiento y su eficiencia. Entre otras. Y dame el resumen completo antes de empezar a modificar algo." | Diagnóstico de legibilidad, escalabilidad, rendimiento y robustez, con un plan de 9 refactorizaciones ordenadas de menor a mayor riesgo. Estado inicial: `pytest` 20/20 y `ruff check src` con 20 errores. |

## Refactorizaciones

| #  | Prompt usado | Cambio realizado | Justificación | Tests OK |
|----|--------------|------------------|---------------|----------|
| 1  | "Eliminemos codigo muerto: funciones viejas, bloques comentados, modo_debug, import os, lineas coding. Y validemos con pytest y ruff check src, haz un commit por cada refactorizacion que vayamos aplicando, con lo realizado." | Se eliminaron `calcular_descuento_viejo`, el bloque comentado `exportar_txt`, `MODO_DEBUG`, `reporteViejoCSV`, el `import os` sin usar y las 4 líneas `# -*- coding: utf-8 -*-`. Antes se verificó que nada se referenciara en `src/` ni en `tests/`. Commit `cee90d2`. | El código muerto confunde ("¿esto se usa?") y hay que mantenerlo sin que aporte nada; el historial de git ya conserva lo eliminado "por si acaso". | ✅ 20/20<br>ruff 20 → 13 |
| 2  | "Ahora apliquemos para mejorar la legibilidad: Constantes de negocio para tasas, umbrales, IVA, prefijo VIP y stock mínimo" | Sección "Reglas de negocio" en `gestor.py` con `MONTO_/TASA_DESCUENTO_ALTO` y `_MEDIO`, `PREFIJO_CLIENTE_VIP`, `MONTO_MINIMO_VIP`, `TASA_DESCUENTO_VIP` y `TASA_IVA`, y `STOCK_MINIMO` en `reportes.py`. Reemplazan los literales en `registrar_venta`, `cotizar` y los dos reportes. Commit `57f9f96`. | Las reglas se entienden por su nombre y no por un número suelto. Antes los valores estaban copiados en varias funciones; ahora cambiar una tasa o un umbral se hace en un solo lugar. | ✅ 20/20<br>ruff 13 → 13 |
| 3  | "Procedamos con Extraer el cálculo de precio a una sola función (subtotal → descuento → IVA → total), usada por registrar_venta y cotizar." | Nueva función `calcular_precio(precio_unitario, cantidad, cliente)`, apoyada en `_descuento_por_volumen` (retornos tempranos) y `_es_cliente_vip` (`startswith`). `registrar_venta` y `cotizar` la usan; `cotizar` sigue sin aplicar VIP, como antes. Commit `1c0b827`. | Elimina la lógica duplicada: un cambio de tasa ya no puede quedar aplicado en una función y olvidado en la otra. Las condiciones anidadas quedaron como funciones cortas con nombre, y el cálculo se puede probar sin registrar una venta. | ✅ 20/20<br>ruff 13 → 8 |
| 4  | "Realizemos Dividir registrar_venta: validación con retornos tempranos, cálculo, ticket y registro." | `registrar_venta` se dividió en `_validar_venta` (4 retornos tempranos en lugar de 4 `if/else` anidados), `_crear_venta` (diccionario literal con el mismo orden de llaves) y `_armar_ticket` (lista de líneas, f-strings y `join`). La función principal quedó en unas 15 líneas. Commit `7887f7c`. | Cada función tiene una sola responsabilidad. Las validaciones se leen de arriba abajo sin anidamiento, el formato del ticket se cambia sin tocar la lógica de la venta, y unir una lista de líneas es más claro y eficiente que concatenar texto. | ✅ 20/20<br>ruff 8 → 8 |
| 5  | "Persistencia segura: with, excepción específica (ValueError), hay_archivo simplificado, carga con update/extend" | En `almacen.py`: archivos abiertos con `with`, `except ValueError` en lugar de `except Exception`, carga con `INVENTARIO.update()` y `VENTAS.extend()`, y `hayArchivo` renombrada a `hay_archivo` en una línea. Se actualizaron `main.py` y `CLAUDE.md`. Commit `61ef90d`. | Los archivos se cierran siempre, aunque ocurra un error. Solo se atrapan los errores esperados (JSON inválido o archivo que no es UTF-8, ambos heredan de `ValueError`) sin ocultar fallos reales del programa. Los nombres siguen PEP 8. | ✅ 20/20<br>ruff 8 → 3 |
| 6  | "Nombres descriptivos y consistentes: contador_ventas (actualizando almacen), aux/temp2/x → nombres claros" | `contadorVentas` → `contador_ventas` (también en `almacen.py`), `hacer_cosa` → `formatear_dinero` y unas 30 variables renombradas en los 4 módulos (`aux` → `nuevo_stock`/`valor_total`, `temp2` → `encontrados`/`bajos`, `op` → `opcion`, `par[0]` → `codigo`…). Se conservaron los nombres que usan los tests. Commit `af09e5e`. | El código se entiende sin adivinar qué guarda cada variable; por ejemplo, `aux` significaba tres cosas distintas según el archivo. Todo queda en snake_case (PEP 8), salvo `agregarProducto` y `buscarProducto`, que exigen los tests. | ✅ 20/20<br>ruff 3 → 2 |
| 7  | "Type hints en todas las funciones" | Las 24 funciones, las variables globales y las locales ambiguas quedaron anotadas, con alias `Producto`, `Venta` y `Montos` y sintaxis `X \| None` de Python 3.10. Se verificó con `mypy --strict`, instalado fuera del proyecto. Commit `24acc35`. | Las firmas documentan qué recibe y qué devuelve cada función, y el editor y mypy detectan usos incorrectos antes de ejecutar. mypy obligó a hacer explícito, con un `assert`, que un valor ya había sido validado. | ✅ 20/20<br>ruff 2 → 2<br>mypy sin errores |
| 8  | "Dividir menu: una función por opción y un diccionario de opciones a funciones" | El `if/elif` de 8 ramas de `menu()` se convirtió en una función por opción y una tabla `OPCIONES` (tecla → texto y función) desde la que se genera el menú. `_mostrar_error()` reemplaza un `print` repetido 3 veces. Se ordenaron los imports. Commit `2d579ad`. | La complejidad de `menu` bajó de 17 a un ciclo simple. Cada opción se lee por separado, y agregar una opción es agregar una fila a la tabla sin tocar el ciclo principal. | ✅ 20/20<br>**ruff 2 → 0** |

> Agrega más filas si realizas más de 5 refactorizaciones.

### Validación adicional

Además de `pytest` y `ruff check src`, después de cada refactorización se comparó
el comportamiento del código nuevo contra el anterior con scripts fuera del
repositorio. Los resultados fueron idénticos en todos los casos:

- **Ventas y cotizaciones:** 960 combinaciones de precio, cantidad y tipo de cliente,
  incluidos los casos límite (justo 500 y 1000, VIP cerca de 200, `"vip"` en
  minúsculas, cliente `None`). Se compararon todos los campos de la venta, el ticket
  y todos los mensajes de error.
- **Persistencia:** bytes exactos del JSON guardado, ida y vuelta de los datos,
  continuidad del folio y archivos inexistente, inválido, vacío, en latin-1 y sin
  `"contador"`.
- **Reportes:** texto completo de los 5 reportes, con y sin ventas.
- **Menú interactivo:** una sesión completa con entradas simuladas que pasa por las 8
  opciones, entradas inválidas y errores; se compararon las 145 líneas de salida y el
  JSON guardado.

**Estado final:** `pytest` 20/20 y `ruff check src` sin errores. No se modificó
ningún archivo de `tests/` ni `pyproject.toml`.

## Reflexión final (10-15 líneas)

Responde: ¿Qué tan útil fue Claude Code para detectar y corregir los problemas?
¿Qué propuso la IA que tú no habías notado? ¿En qué casos tuviste que corregir
o rechazar sus sugerencias? ¿Qué aprendiste sobre refactorizar con apoyo de IA?

*(Escribe aquí tu reflexión)*
