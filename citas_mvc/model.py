"""
model.py — Capa Modelo (M en MVC)
Responsabilidad: datos en memoria + reglas de negocio + validaciones.
Sin base de datos: todo vive en la lista `_citas`.
"""

import re
from datetime import date, datetime, timedelta

# ── Almacenamiento en memoria ──────────────────────────────────
_citas   = []
_next_id = 1

# ── Datos de ejemplo ──────────────────────────────────────────
def _seed():
    global _citas, _next_id

    _citas   = []
    _next_id = 1

    ejemplos = [
        ("Ana Pérez Torres",     1, "09:00", "Consulta general"),
        ("Carlos Quispe Mamani", 1, "09:30", "Revisión de resultados"),
        ("Lucía Vargas Flores",  2, "10:00", "Primera consulta"),
        ("Roberto Díaz Luna",    2, "14:00", "Control mensual"),
        ("María Flores Cano",    3, "08:00", "Urgencia leve"),
    ]

    for nombre, dias, hora, motivo in ejemplos:
        d = date.today()
        guardar({
            "nombre_cliente": nombre,
            "fecha": str(d + timedelta(days=dias)),
            "hora":  hora,
            "motivo": motivo,
        })

    # Cita cancelada de ejemplo
    _citas.append({
        "id": _next_id,
        "nombre_cliente": "Pedro Salinas",
        "fecha": str(date.today()),
        "hora":  "11:00",
        "motivo": "Cita de prueba cancelada",
        "estado": "cancelada",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    _next_id += 1


# ── Validaciones ──────────────────────────────────────────────
def _validar(datos, excluir_id=None):
    errores = {}

    nombre = str(datos.get("nombre_cliente", "")).strip()
    fecha  = str(datos.get("fecha", "")).strip()
    hora   = str(datos.get("hora", "")).strip()
    motivo = str(datos.get("motivo", "")).strip()

    if not nombre:
        errores["nombre_cliente"] = "El nombre es requerido."
    elif len(nombre) < 3:
        errores["nombre_cliente"] = "Mínimo 3 caracteres."
    elif len(nombre) > 100:
        errores["nombre_cliente"] = "Máximo 100 caracteres."
    elif not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'\-]+$", nombre):
        errores["nombre_cliente"] = "Solo letras y espacios."

    if not fecha:
        errores["fecha"] = "La fecha es requerida."
    else:
        try:
            f = datetime.strptime(fecha, "%Y-%m-%d").date()
            if f < date.today():
                errores["fecha"] = "No se permiten fechas pasadas."
            elif f.weekday() == 6:
                errores["fecha"] = "No domingos."
        except ValueError:
            errores["fecha"] = "Formato inválido."

    if not hora:
        errores["hora"] = "La hora es requerida."
    else:
        try:
            h = datetime.strptime(hora, "%H:%M")
            if not (8 <= h.hour < 20):
                errores["hora"] = "Horario 08:00–19:30."
            elif h.minute not in (0, 30):
                errores["hora"] = "Solo :00 o :30."
        except ValueError:
            errores["hora"] = "Formato inválido."

    if not motivo:
        errores["motivo"] = "El motivo es requerido."
    elif len(motivo) < 5:
        errores["motivo"] = "Mínimo 5 caracteres."
    elif len(motivo) > 255:
        errores["motivo"] = "Máximo 255 caracteres."

    if "fecha" not in errores and "hora" not in errores:
        for c in _citas:
            if c["id"] == excluir_id:
                continue
            if c["fecha"] == fecha and c["hora"] == hora and c["estado"] == "activa":
                errores["hora"] = f"Horario ocupado (ID {c['id']})."
                break

    return errores


# ── Operaciones ───────────────────────────────────────────────
def guardar(datos):
    global _next_id

    errores = _validar(datos)
    if errores:
        return None, errores

    cita = {
        "id": _next_id,
        "nombre_cliente": datos["nombre_cliente"].strip(),
        "fecha": datos["fecha"].strip(),
        "hora": datos["hora"].strip(),
        "motivo": datos["motivo"].strip(),
        "estado": "activa",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    _citas.append(cita)
    _next_id += 1
    return cita, {}


def buscar(id_cita=None, nombre=None):
    if not id_cita and not nombre:
        return [], "Debe ingresar ID o nombre."

    if id_cita:
        try:
            n = int(id_cita)
            if n <= 0:
                raise ValueError
        except:
            return [], "ID inválido."

        resultado = [c for c in _citas if c["id"] == n]
    else:
        q = str(nombre).strip()
        if len(q) < 2:
            return [], "Mínimo 2 caracteres."

        resultado = [c for c in _citas if q.lower() in c["nombre_cliente"].lower()]

    if not resultado:
        return [], "No se encontraron citas."

    return resultado, None


def listar(fecha=None, estado=None):
    if estado not in ("activa", "cancelada", None, ""):
        return [], "Estado inválido."

    resultado = list(_citas)

    if fecha:
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            return [], "Fecha inválida."
        resultado = [c for c in resultado if c["fecha"] == fecha]

    if estado:
        resultado = [c for c in resultado if c["estado"] == estado]

    resultado.sort(key=lambda c: (c["fecha"], c["hora"]))
    return resultado, None


def snapshot():
    return {
        "total_registros": len(_citas),
        "siguiente_id": _next_id,
        "citas": list(_citas),
    }


# ── Inicialización ────────────────────────────────────────────
_seed()