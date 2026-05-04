from flask import Blueprint, request, jsonify
import model

citas_bp = Blueprint("citas", __name__)

# ── RF-01: Registrar ─────────────────────────────
@citas_bp.route("/api/citas", methods=["POST"])
def registrar():
    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({"success": False, "error": "JSON inválido"}), 400

    cita, error = model.guardar(datos)

    if error:
        return jsonify({"success": False, "error": error}), 400

    return jsonify({
        "success": True,
        "cita": cita
    }), 201


# ── RF-02: Buscar ────────────────────────────────
@citas_bp.route("/api/citas/buscar", methods=["GET"])
def buscar():
    id_cita = request.args.get("id")
    nombre  = request.args.get("nombre")

    citas, error = model.buscar(id_cita, nombre)

    if error:
        return jsonify({"success": False, "error": error}), 400

    return jsonify({
        "success": True,
        "total": len(citas),
        "citas": citas
    })


# ── RF-05: Listar agenda ─────────────────────────
@citas_bp.route("/api/citas", methods=["GET"])
def listar():
    fecha  = request.args.get("fecha")
    estado = request.args.get("estado")

    citas, _ = model.listar(fecha, estado)

    return jsonify({
        "success": True,
        "total": len(citas),
        "citas": citas
    })


# ── Cancelar ─────────────────────────────────────
@citas_bp.route("/api/citas/cancelar/<int:id>", methods=["PUT"])
def cancelar(id):
    cita, _ = model.cancelar(id)
    return jsonify({"success": True, "cita": cita})


# ── Reasignar ────────────────────────────────────
@citas_bp.route("/api/citas/reasignar/<int:id>", methods=["PUT"])
def reasignar(id):
    datos = request.get_json()

    cita, error = model.reasignar(id, datos["fecha"], datos["hora"])

    if error:
        return jsonify({"success": False, "error": error}), 400

    return jsonify({"success": True, "cita": cita})


# ── DEBUG  ───────────────────
@citas_bp.route("/api/modelo", methods=["GET"])
def modelo():
    citas, _ = model.listar()
    return jsonify({
        "total": len(citas),
        "citas": citas
    })


# ── RESET ───────────────────────────────────────
@citas_bp.route("/api/reset", methods=["POST"])
def reset():
    import os
    if os.path.exists("citas.db"):
        os.remove("citas.db")
    model.crear_tabla()
    return jsonify({"success": True})