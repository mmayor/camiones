import re
from string import ascii_uppercase
from app.models import Factura

def generar_numero_factura(direccion):
    # Extraer primer número (se asume que está al inicio)
    match = re.match(r"(\d+)", direccion.strip())
    if not match:
        raise ValueError("La dirección no comienza con un número válido")
    base_num = match.group(1)

    # Buscar si ya hay facturas con ese número o variantes (ejemplo: '1850', '1850A', '1850B'...)
    existentes = Factura.query.filter(Factura.numero.like(f"{base_num}%")).all()
    existentes_numeros = [f.numero for f in existentes]

    if base_num not in existentes_numeros:
        return base_num  # Número sin letra aún disponible

    # Si base_num existe, añadir letra
    for letra in ascii_uppercase:
        nuevo_num = f"{base_num}{letra}"
        if nuevo_num not in existentes_numeros:
            return nuevo_num

    raise ValueError("No se pudo generar número único para la factura")

