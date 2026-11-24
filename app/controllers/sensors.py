from flask import Blueprint, request
from ..extensions import db
from ..models import Device, Sensor
from ..utils import error, get_json_object, required_text, numeric_value, success

sensors_bp = Blueprint("sensors", __name__, url_prefix="/api/sensors")

def thresholds(payload, current=None):
    low = payload.get("min_threshold", current.min_threshold if current else None)
    high = payload.get("max_threshold", current.max_threshold if current else None)
    low = None if low is None else numeric_value(low, "min_threshold")
    high = None if high is None else numeric_value(high, "max_threshold")
    if low is not None and high is not None and low >= high:
        raise ValueError("min_threshold harus lebih kecil dari max_threshold.")
    return low, high

@sensors_bp.get("")
def list_sensors():
    query = Sensor.query
    if request.args.get("device_id"):
        try: query = query.filter_by(device_id=int(request.args["device_id"]))
        except ValueError: return error("device_id harus berupa integer.")
    return success([x.to_dict() for x in query.order_by(Sensor.id.asc()).all()])

@sensors_bp.post("")
def create_sensor():
    payload = get_json_object()
    if payload is None: return error("Body harus berupa JSON object.")
    try:
        device_id = int(payload.get("device_id"))
        if device_id < 1: raise ValueError
    except (TypeError, ValueError): return error("device_id harus berupa integer positif.")
    if not db.session.get(Device, device_id): return error("Device tidak ditemukan.", 404)
    try:
        low, high = thresholds(payload)
        row = Sensor(device_id=device_id, name=required_text(payload, "name"),
                     sensor_type=required_text(payload, "sensor_type", 50),
                     unit=required_text(payload, "unit", 20), min_threshold=low,
                     max_threshold=high, is_active=payload.get("is_active", True))
        if not isinstance(row.is_active, bool): return error("is_active harus boolean.")
        db.session.add(row); db.session.commit()
        return success(row.to_dict(), "Sensor berhasil dibuat.", 201)
    except ValueError as exc: return error(str(exc))

@sensors_bp.get("/<int:sensor_id>")
def get_sensor(sensor_id):
    row = db.session.get(Sensor, sensor_id)
    if not row: return error("Sensor tidak ditemukan.", 404)
    return success(row.to_dict())

@sensors_bp.put("/<int:sensor_id>")
def update_sensor(sensor_id):
    row = db.session.get(Sensor, sensor_id)
    if not row: return error("Sensor tidak ditemukan.", 404)
    payload = get_json_object()
    if payload is None: return error("Body harus berupa JSON object.")
    try:
        for key, max_len in (("name", 120), ("sensor_type", 50), ("unit", 20)):
            if key in payload: setattr(row, key, required_text(payload, key, max_len))
        low, high = thresholds(payload, row)
        row.min_threshold, row.max_threshold = low, high
        if "is_active" in payload:
            if not isinstance(payload["is_active"], bool): return error("is_active harus boolean.")
            row.is_active = payload["is_active"]
        db.session.commit(); return success(row.to_dict(), "Sensor berhasil diperbarui.")
    except ValueError as exc: db.session.rollback(); return error(str(exc))

@sensors_bp.delete("/<int:sensor_id>")
def delete_sensor(sensor_id):
    row = db.session.get(Sensor, sensor_id)
    if not row: return error("Sensor tidak ditemukan.", 404)
    db.session.delete(row); db.session.commit()
    return success({"id": sensor_id}, "Sensor berhasil dihapus.")
