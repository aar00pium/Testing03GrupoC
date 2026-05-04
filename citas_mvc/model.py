import sqlite3
import re
from datetime import datetime

DB = "citas.db"

def get_conn():
    return sqlite3.connect(DB)

def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cliente TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            motivo TEXT NOT NULL,
            estado TEXT NOT NULL
        )
        """)

def validar(datos):
    errores = {}

    nombre = (datos.get("nombre_cliente") or "").strip()
    fecha = datos.get("fecha")
    hora = datos.get("hora")
    motivo = (datos.get("motivo") or "").strip()

    if not nombre or len(nombre) > 100:
        errores["nombre_cliente"] = "Nombre inválido"

    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(fecha)):
        errores["fecha"] = "Fecha inválida"

    if not re.match(r"^\d{2}:\d{2}$", str(hora)):
        errores["hora"] = "Hora inválida"

    if not motivo or len(motivo) > 255:
        errores["motivo"] = "Motivo inválido"

    if errores:
        return errores

    try:
        f = datetime.strptime(fecha, "%Y-%m-%d").date()
        if f < datetime.now().date():
            errores["fecha"] = "Fecha pasada"
    except:
        errores["fecha"] = "Fecha inválida"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM citas WHERE fecha=? AND hora=? AND estado='activa'",
            (fecha, hora)
        )
        if cur.fetchone():
            errores["hora"] = "Horario ocupado"

    return errores

def guardar(datos):
    error = validar(datos)
    if error:
        return None, error

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO citas(nombre_cliente, fecha, hora, motivo, estado)
        VALUES (?, ?, ?, ?, 'activa')
        """, (
            datos["nombre_cliente"].strip(),
            datos["fecha"],
            datos["hora"],
            datos["motivo"].strip()
        ))
        conn.commit()

        return {
            "id": cur.lastrowid,
            **datos,
            "estado": "activa"
        }, None

def listar(fecha=None, estado=None):
    query = "SELECT * FROM citas WHERE 1=1"
    params = []

    if fecha:
        query += " AND fecha=?"
        params.append(fecha)

    if estado:
        query += " AND estado=?"
        params.append(estado)

    query += " ORDER BY fecha, hora"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()

    return [dict(zip(
        ["id","nombre_cliente","fecha","hora","motivo","estado"], r
    )) for r in rows], None

def buscar(id_cita=None, nombre=None):
    with get_conn() as conn:
        cur = conn.cursor()

        if id_cita:
            cur.execute("SELECT * FROM citas WHERE id=?", (id_cita,))
        else:
            cur.execute("SELECT * FROM citas WHERE nombre_cliente LIKE ?", (f"%{nombre}%",))

        rows = cur.fetchall()

    return [dict(zip(
        ["id","nombre_cliente","fecha","hora","motivo","estado"], r
    )) for r in rows], None

def cancelar(id_cita):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE citas SET estado='cancelada' WHERE id=?", (id_cita,))
        conn.commit()

    return True, None

def reasignar(id_cita, fecha, hora):
    if not fecha or not hora:
        return None, "Datos inválidos"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE citas SET fecha=?, hora=? WHERE id=?", (fecha, hora, id_cita))
        conn.commit()

    return True, None