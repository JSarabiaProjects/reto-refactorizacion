"""Persistencia del gestor: carga y guardado de datos en JSON."""

import json
import os

import gestor


def guardar_datos(ruta):
    """Guarda el inventario, las ventas y el folio actual en un JSON."""
    datos = {
        "inventario": gestor.INVENTARIO,
        "ventas": gestor.VENTAS,
        "contador": gestor.contador_ventas,
    }
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=2, ensure_ascii=False)
    return True


def cargar_datos(ruta):
    """Lee el archivo JSON y deja los datos en el estado global.

    Regresa False si el archivo no existe o esta corrupto.
    """
    if not hay_archivo(ruta):
        gestor.ultimo_error = "el archivo no existe"
        return False
    try:
        with open(ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except ValueError:
        # JSONDecodeError (JSON invalido) y UnicodeDecodeError (no es texto
        # UTF-8) heredan de ValueError
        gestor.ultimo_error = "archivo corrupto"
        return False
    gestor.INVENTARIO.clear()
    gestor.INVENTARIO.update(datos["inventario"])
    gestor.VENTAS.clear()
    gestor.VENTAS.extend(datos["ventas"])
    gestor.contador_ventas = datos.get("contador", 0)
    return True


def hay_archivo(ruta):
    """Indica si ya existe el archivo de datos."""
    return os.path.exists(ruta)
