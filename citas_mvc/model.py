import sqlite3
from datetime import datetime

DB = "citas.db"

def conectar():
    return sqlite3.connect(DB)


def crear_tabla():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_cliente TEXT NOT NULL,
        fecha TEXT NOT NULL,
        hora TEXT NOT NULL,
        motivo TEXT NOT NULL,
        estado TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# ── VALIDAR ──
def validar(datos):
    if not datos:
        return "JSON vacío"

    campos = ["nombre_cliente", "fecha", "hora", "motivo"]
    for c in campos:
        if not datos.get(c):
            return f"Falta {c}"

    try:
        datetime.strptime(datos["fecha"], "%Y-%m-%d")
        datetime.strptime(datos["hora"], "%H:%M")
    except:
        return "Fecha u hora inválida"

    return None


# ── GUARDAR ──
def guardar(datos):
    error = validar(datos)
    if error:
        return None, error

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO citas (nombre_cliente, fecha, hora, motivo, estado)
    VALUES (?, ?, ?, ?, 'activa')
    """, (
        datos["nombre_cliente"],
        datos["fecha"],
        datos["hora"],
        datos["motivo"]
    ))

    conn.commit()
    id = cursor.lastrowid
    conn.close()

    return {"id": id, **datos, "estado": "activa"}, None


# ── LISTAR (RF-05 BIEN) ──
def listar(fecha=None, estado=None):
    conn = conectar()
    cursor = conn.cursor()

    query = "SELECT * FROM citas WHERE 1=1"
    params = []

    if fecha:
        query += " AND fecha=?"
        params.append(fecha)

    if estado:
        query += " AND estado=?"
        params.append(estado)

    query += " ORDER BY fecha, hora"

    cursor.execute(query, params)
    datos = cursor.fetchall()
    conn.close()

    return [
        {
            "id": d[0],
            "nombre_cliente": d[1],
            "fecha": d[2],
            "hora": d[3],
            "motivo": d[4],
            "estado": d[5]
        }
        for d in datos
    ], None


# ── BUSCAR ──
def buscar(id_cita=None, nombre=None):
    conn = conectar()
    cursor = conn.cursor()

    if id_cita:
        cursor.execute("SELECT * FROM citas WHERE id=?", (id_cita,))
    elif nombre:
        cursor.execute("SELECT * FROM citas WHERE nombre_cliente LIKE ?", (f"%{nombre}%",))
    else:
        return [], "Debe buscar algo"

    datos = cursor.fetchall()
    conn.close()

    return [
        {
            "id": d[0],
            "nombre_cliente": d[1],
            "fecha": d[2],
            "hora": d[3],
            "motivo": d[4],
            "estado": d[5]
        }
        for d in datos
    ], None


# ── CANCELAR ──
def cancelar(id_cita):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("UPDATE citas SET estado='cancelada' WHERE id=?", (id_cita,))
    conn.commit()
    conn.close()

    return {"id": id_cita, "estado": "cancelada"}, None


# ── REASIGNAR ──
def reasignar(id_cita, fecha, hora):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE citas SET fecha=?, hora=? WHERE id=?
    """, (fecha, hora, id_cita))

    conn.commit()
    conn.close()

    return {"id": id_cita, "fecha": fecha, "hora": hora}, None


crear_tabla()