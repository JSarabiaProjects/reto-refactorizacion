"""Reportes de la tienda: inventario, ventas y mas vendidos."""

import gestor

# Un producto con menos unidades que este minimo se reporta como stock bajo
STOCK_MINIMO = 5


def formatear_dinero(monto):
    """Da formato de dinero a un monto, redondeado a 2 decimales."""
    return "$" + str(round(monto, 2))


def productos_stock_bajo():
    """Regresa la lista de productos con stock por debajo del minimo."""
    bajos = []
    for producto in gestor.INVENTARIO.values():
        if producto["stock"] < STOCK_MINIMO:
            bajos.append(producto)
    return bajos


def reporte_inventario():
    """Arma el reporte del inventario, lo imprime y lo regresa como texto."""
    reporte = "===== INVENTARIO =====\n"
    valor_total = 0
    for producto in gestor.INVENTARIO.values():
        linea = producto["codigo"] + " | " + producto["nombre"] + " | "
        linea = linea + formatear_dinero(producto["precio"])
        linea = linea + " | stock: " + str(producto["stock"])
        if producto["stock"] < STOCK_MINIMO:
            linea = linea + "  <-- STOCK BAJO"
        reporte = reporte + linea + "\n"
        valor_total = valor_total + producto["precio"] * producto["stock"]
    reporte = reporte + "Valor total del inventario: "
    reporte = reporte + formatear_dinero(valor_total) + "\n"
    print(reporte)
    return reporte


def total_vendido():
    """Suma el total (con IVA) de todas las ventas registradas."""
    total = 0
    for venta in gestor.VENTAS:
        total = total + venta["total"]
    return round(total, 2)


def mas_vendidos(n=3):
    """Regresa los n productos mas vendidos como lista de (codigo, unidades)."""
    unidades_por_codigo = {}
    for venta in gestor.VENTAS:
        codigo = venta["codigo"]
        if codigo in unidades_por_codigo:
            unidades_por_codigo[codigo] = (
                unidades_por_codigo[codigo] + venta["cantidad"]
            )
        else:
            unidades_por_codigo[codigo] = venta["cantidad"]
    ranking = list(unidades_por_codigo.items())
    # ordenamiento de burbuja (TODO: algun dia usar sorted)
    for i in range(len(ranking)):
        for j in range(0, len(ranking) - i - 1):
            if ranking[j][1] < ranking[j + 1][1]:
                ranking[j], ranking[j + 1] = ranking[j + 1], ranking[j]
    return ranking[0:n]


def resumen_ventas():
    """Arma el resumen de ventas del dia, lo imprime y lo regresa."""
    resumen = "===== RESUMEN DE VENTAS =====\n"
    total = 0
    for venta in gestor.VENTAS:
        resumen = resumen + "Folio " + str(venta["folio"]) + ": " + venta["nombre"]
        resumen = resumen + " x" + str(venta["cantidad"]) + " = "
        resumen = resumen + formatear_dinero(venta["total"]) + "\n"
        total = total + venta["total"]
    resumen = resumen + "Numero de ventas: " + str(len(gestor.VENTAS)) + "\n"
    resumen = resumen + "Total del dia: " + formatear_dinero(total) + "\n"
    print(resumen)
    return resumen
