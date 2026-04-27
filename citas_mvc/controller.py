"""
controller.py — Capa Controlador (C en MVC)
Responsabilidad: recibir las peticiones HTTP, llamar al Modelo
y devolver la respuesta JSON a la Vista.
NO contiene lógica de negocio (esa vive en model.py).
"""

from flask import Blueprint, request, jsonify
import model

citas_bp = Blueprint("citas", __name__)


# ── RF-01: Registrar cita ─────────────────────────────────────
@citas_bp.route("/api/citas", methods=["POST"])
def registrar():
    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({"success": False, "error": "El cuerpo debe ser JSON válido."}), 400

    cita, errores = model.guardar(datos)

    if errores:
        return jsonify({"success": False, "errores": errores}), 422

    return jsonify({"success": True, "mensaje": "Cita registrada.", "cita": cita}), 201


# ── RF-02: Consultar cita ─────────────────────────────────────
@citas_bp.route("/api/citas/buscar", methods=["GET"])
def consultar():
    id_cita = request.args.get("id", "").strip()
    nombre  = request.args.get("nombre", "").strip()

    resultado, error = model.buscar(
        id_cita=id_cita or None,
        nombre=nombre or None,
    )

    if error:
        return jsonify({"success": False, "error": error}), 404 if "No se encontraron" in error else 400

    return jsonify({"success": True, "total": len(resultado), "citas": resultado}), 200


# ── RF-05: Listar agenda ──────────────────────────────────────
@citas_bp.route("/api/citas", methods=["GET"])
def listar():
    fecha  = request.args.get("fecha", "").strip() or None
    estado = request.args.get("estado", "").strip() or None

    resultado, error = model.listar(fecha=fecha, estado=estado)

    if error:
        return jsonify({"success": False, "error": error}), 422

    return jsonify({
        "success": True,
        "total":   len(resultado),
        "citas":   resultado,
    }), 200


# ── Snapshot del modelo (depuración) ─────────────────────────
@citas_bp.route("/api/modelo", methods=["GET"])
def ver_modelo():
    return jsonify(model.snapshot()), 200


# ── Reset de datos de ejemplo ─────────────────────────────────
@citas_bp.route("/api/reset", methods=["POST"])
def reset():
    model._seed()
    return jsonify({"success": True, "mensaje": "Datos reseteados."}), 200