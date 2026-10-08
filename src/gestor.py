"""Modulo principal del gestor de inventario y ventas de "La Esquina".

Aqui vive casi toda la logica del negocio. Historicamente este archivo
lo fueron parchando varias personas, asi que hay de todo un poco.
"""

from datetime import datetime

# ---------------------------------------------------------------
# Reglas de negocio (tasas expresadas como fraccion: 0.10 = 10 %)
# ---------------------------------------------------------------
# Descuento por volumen segun el subtotal de la compra
MONTO_DESCUENTO_ALTO = 1000
TASA_DESCUENTO_ALTO = 0.10
MONTO_DESCUENTO_MEDIO = 500
TASA_DESCUENTO_MEDIO = 0.05
# Descuento extra para clientes VIP, aplicado sobre el subtotal cuando la
# compra (ya con el descuento por volumen) supera el monto minimo
PREFIJO_CLIENTE_VIP = "VIP"
MONTO_MINIMO_VIP = 200
TASA_DESCUENTO_VIP = 0.02
TASA_IVA = 0.16

# ---------------------------------------------------------------
# Estado global de la aplicacion (inventario, ventas y contadores)
# ---------------------------------------------------------------
INVENTARIO = {}
VENTAS = []
contadorVentas = 0
ultimo_error = ""


def reiniciar_sistema():
    """Borra todo el estado del sistema (inventario, ventas y folios)."""
    global contadorVentas, ultimo_error
    INVENTARIO.clear()
    VENTAS.clear()
    contadorVentas = 0
    ultimo_error = ""


def agregarProducto(codigo, nombre, precio, stock):
    # valida los datos y da de alta un producto en el inventario
    global ultimo_error
    if codigo is None or codigo == "":
        ultimo_error = "codigo vacio"
        return False
    if codigo in INVENTARIO:
        ultimo_error = "el producto ya existe"
        return False
    if precio <= 0:
        ultimo_error = "precio invalido"
        return False
    if stock < 0:
        ultimo_error = "stock invalido"
        return False
    x = {}
    x["codigo"] = codigo
    x["nombre"] = nombre
    x["precio"] = precio
    x["stock"] = stock
    INVENTARIO[codigo] = x
    return True


def eliminar_producto(codigo):
    """Quita un producto del inventario. Regresa False si no existe."""
    global ultimo_error
    if codigo in INVENTARIO:
        del INVENTARIO[codigo]
        return True
    ultimo_error = "producto no existe"
    return False


def actualizar_stock(codigo, cantidad):
    """Suma unidades al stock (o resta si la cantidad es negativa)."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return False
    aux = INVENTARIO[codigo]["stock"] + cantidad
    if aux < 0:
        ultimo_error = "el stock no puede quedar negativo"
        return False
    INVENTARIO[codigo]["stock"] = aux
    return True


def buscarProducto(texto):
    # busca productos cuyo nombre contenga el texto (sin importar mayusculas)
    temp2 = []
    for k in INVENTARIO:
        if texto.lower() in INVENTARIO[k]["nombre"].lower():
            temp2.append(INVENTARIO[k])
    return temp2


def _descuento_por_volumen(subtotal):
    """Regresa el descuento que corresponde al subtotal de la compra."""
    if subtotal >= MONTO_DESCUENTO_ALTO:
        return subtotal * TASA_DESCUENTO_ALTO
    if subtotal >= MONTO_DESCUENTO_MEDIO:
        return subtotal * TASA_DESCUENTO_MEDIO
    return 0


def _es_cliente_vip(cliente):
    """Un cliente es VIP si su codigo empieza con el prefijo VIP."""
    return bool(cliente) and cliente.startswith(PREFIJO_CLIENTE_VIP)


def calcular_precio(precio_unitario, cantidad, cliente=""):
    """Calcula subtotal, descuento, IVA y total de una compra.

    Los clientes VIP reciben un descuento extra sobre el subtotal, pero solo
    si su compra (ya con el descuento por volumen) supera el monto minimo.
    Solo el total se regresa redondeado a 2 decimales; los demas montos se
    regresan sin redondear para que quien los use decida como mostrarlos.
    """
    subtotal = precio_unitario * cantidad
    descuento = _descuento_por_volumen(subtotal)
    if _es_cliente_vip(cliente) and subtotal - descuento > MONTO_MINIMO_VIP:
        descuento += subtotal * TASA_DESCUENTO_VIP
    base = subtotal - descuento
    impuesto = base * TASA_IVA
    return {
        "subtotal": subtotal,
        "descuento": descuento,
        "impuesto": impuesto,
        "total": round(base + impuesto, 2),
    }


def _validar_venta(codigo, cantidad):
    """Regresa el motivo por el que la venta no procede, o None si es valida."""
    if codigo is None or codigo == "":
        return "codigo vacio"
    if codigo not in INVENTARIO:
        return "producto no existe"
    if cantidad is None or cantidad <= 0:
        return "cantidad invalida"
    if INVENTARIO[codigo]["stock"] < cantidad:
        return "stock insuficiente"
    return None


def _crear_venta(folio, codigo, nombre, cantidad, cliente, montos):
    """Arma el registro de una venta con los montos redondeados a 2 decimales."""
    return {
        "folio": folio,
        "codigo": codigo,
        "nombre": nombre,
        "cantidad": cantidad,
        "subtotal": round(montos["subtotal"], 2),
        "descuento": round(montos["descuento"], 2),
        "impuesto": round(montos["impuesto"], 2),
        "total": montos["total"],
        "cliente": cliente,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _armar_ticket(venta):
    """Arma el ticket en texto plano; la linea de descuento es opcional."""
    lineas = [
        "TIENDA LA ESQUINA",
        "----------------------------",
        f"Folio: {venta['folio']}",
        f"{venta['nombre']} x{venta['cantidad']}",
        f"Subtotal: ${venta['subtotal']}",
    ]
    if venta["descuento"] > 0:
        lineas.append(f"Descuento: -${venta['descuento']}")
    lineas.append(f"IVA: ${venta['impuesto']}")
    lineas.append(f"TOTAL: ${venta['total']}")
    return "\n".join(lineas) + "\n"


def registrar_venta(codigo, cantidad, cliente=""):
    """Registra una venta: valida, descuenta el stock, asigna folio y ticket.

    Si la venta no procede regresa None, no modifica nada y deja el motivo
    en ultimo_error.
    """
    global contadorVentas, ultimo_error
    error = _validar_venta(codigo, cantidad)
    if error is not None:
        ultimo_error = error
        return None
    producto = INVENTARIO[codigo]
    montos = calcular_precio(producto["precio"], cantidad, cliente)
    producto["stock"] -= cantidad
    contadorVentas += 1
    venta = _crear_venta(
        contadorVentas, codigo, producto["nombre"], cantidad, cliente, montos
    )
    venta["ticket"] = _armar_ticket(venta)
    VENTAS.append(venta)
    return venta


def cotizar(codigo, cantidad):
    """Calcula cuanto costaria una compra sin registrar la venta."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return None
    if cantidad is None or cantidad <= 0:
        ultimo_error = "cantidad invalida"
        return None
    # la cotizacion no recibe cliente, asi que nunca aplica el descuento VIP
    return calcular_precio(INVENTARIO[codigo]["precio"], cantidad)["total"]
