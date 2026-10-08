"""Punto de entrada del gestor de tienda (menu interactivo en consola)."""

from collections.abc import Callable

import almacen
import gestor
import reportes

ARCHIVO: str = "datos_ejemplo.json"


def pedir_numero(mensaje: str) -> float:
    """Pide un numero al usuario hasta que escriba algo valido."""
    while True:
        respuesta = input(mensaje)
        try:
            return float(respuesta)
        except ValueError:
            print("Eso no es un numero, intenta de nuevo.")


def _mostrar_error() -> None:
    """Muestra el motivo de la ultima operacion que fallo."""
    print("Error:", gestor.ultimo_error)


def agregar_producto() -> None:
    """Pide los datos de un producto y lo da de alta."""
    codigo = input("Codigo: ")
    nombre = input("Nombre: ")
    precio = pedir_numero("Precio: ")
    stock = int(pedir_numero("Stock inicial: "))
    if gestor.agregarProducto(codigo, nombre, precio, stock):
        print("Producto agregado.")
    else:
        _mostrar_error()


def registrar_venta() -> None:
    """Pide los datos de una venta, la registra e imprime el ticket."""
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    cliente = input("Codigo de cliente (enter si no tiene): ")
    venta = gestor.registrar_venta(codigo, cantidad, cliente)
    if venta is not None:
        print(venta["ticket"])
    else:
        _mostrar_error()


def cotizar() -> None:
    """Pide producto y cantidad e imprime el total estimado."""
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    total = gestor.cotizar(codigo, cantidad)
    if total is not None:
        print("Total estimado (con IVA): $" + str(total))
    else:
        _mostrar_error()


def mostrar_mas_vendidos() -> None:
    """Imprime los productos mas vendidos."""
    for codigo, unidades in reportes.mas_vendidos():
        print(codigo, "->", unidades, "unidades")


def mostrar_stock_bajo() -> None:
    """Imprime una alerta por cada producto con stock bajo."""
    bajos = reportes.productos_stock_bajo()
    if not bajos:
        print("No hay productos con stock bajo.")
        return
    for producto in bajos:
        nombre, stock = producto["nombre"], producto["stock"]
        print("OJO:", nombre, "solo tiene", stock, "unidades")


def guardar_y_salir() -> None:
    """Guarda los datos en el archivo antes de terminar."""
    almacen.guardar_datos(ARCHIVO)
    print("Datos guardados. Hasta luego.")


def mostrar_reporte_inventario() -> None:
    """Imprime el reporte de inventario."""
    reportes.reporte_inventario()


def mostrar_resumen_ventas() -> None:
    """Imprime el resumen de ventas."""
    reportes.resumen_ventas()


# Cada opcion del menu: tecla -> (texto que se muestra, accion que ejecuta)
OPCIONES: dict[str, tuple[str, Callable[[], None]]] = {
    "1": ("Agregar producto", agregar_producto),
    "2": ("Registrar venta", registrar_venta),
    "3": ("Cotizar", cotizar),
    "4": ("Reporte de inventario", mostrar_reporte_inventario),
    "5": ("Resumen de ventas", mostrar_resumen_ventas),
    "6": ("Mas vendidos", mostrar_mas_vendidos),
    "7": ("Alertas de stock bajo", mostrar_stock_bajo),
    "8": ("Guardar y salir", guardar_y_salir),
}
# Despues de ejecutar esta opcion el programa termina
OPCION_SALIR = "8"


def _cargar_datos_iniciales() -> None:
    """Carga el archivo de datos si ya existe."""
    if almacen.hay_archivo(ARCHIVO):
        almacen.cargar_datos(ARCHIVO)
        print("Datos cargados de", ARCHIVO)


def _mostrar_opciones() -> None:
    """Imprime las opciones del menu a partir de OPCIONES."""
    print("")
    for tecla, (texto, _accion) in OPCIONES.items():
        print(f"{tecla}) {texto}")


def menu() -> None:
    """Ciclo principal: muestra el menu y ejecuta la opcion elegida."""
    print("Bienvenido al gestor de la tienda La Esquina")
    _cargar_datos_iniciales()
    while True:
        _mostrar_opciones()
        opcion = input("Opcion: ")
        if opcion not in OPCIONES:
            print("Opcion no valida.")
            continue
        _texto, accion = OPCIONES[opcion]
        accion()
        if opcion == OPCION_SALIR:
            break


if __name__ == "__main__":
    menu()
