from flask import Blueprint, request, jsonify
import model

bp = Blueprint("api", __name__)

@bp.route("/api/citas", methods=["POST"])
def registrar():
    datos = request.get_json(force=True, silent=True) or {}
    cita, error = model.guardar(datos)

    if error:
        return jsonify({"success": False, "errores": error}), 400

    return jsonify({"success": True, "cita": cita}), 201

@bp.route("/api/citas", methods=["GET"])
def listar():
    fecha = request.args.get("fecha")
    estado = request.args.get("estado")

    citas, _ = model.listar(fecha, estado)
    return jsonify({"success": True, "citas": citas, "total": len(citas)})

@bp.route("/api/citas/buscar")
def buscar():
    id_cita = request.args.get("id")
    nombre = request.args.get("nombre")

    citas, _ = model.buscar(id_cita, nombre)
    return jsonify({"success": True, "citas": citas, "total": len(citas)})

@bp.route("/api/citas/cancelar/<int:id>", methods=["PUT"])
def cancelar(id):
    model.cancelar(id)
    return jsonify({"success": True})

@bp.route("/api/citas/reasignar/<int:id>", methods=["PUT"])
def reasignar(id):
    datos = request.get_json(force=True, silent=True) or {}
    ok, error = model.reasignar(id, datos.get("fecha"), datos.get("hora"))

    if error:
        return jsonify({"success": False, "error": error}), 400

    return jsonify({"success": True})