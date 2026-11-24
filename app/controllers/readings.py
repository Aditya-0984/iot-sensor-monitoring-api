from datetime import datetime
from flask import Blueprint, request
from sqlalchemy import desc, asc
from ..extensions import db
from ..models import Device, Sensor, Reading, Alert
from ..utils import error, get_json_object, numeric_value, positive_int, parse_datetime, success

readings_bp = Blueprint("readings", __name__, url_prefix="/api/readings")

@readings_bp.post("")
def create_reading():
    payload = get_json_object()
    if payload is None: return error("Body harus berupa JSON object.")
    try:
        sensor_id = positive_int(payload.get("sensor_id"), "sensor_id")
        value = numeric_value(payload.get("value"), "value")
        recorded_at = parse_datetime(payload.get("recorded_at"))
    except ValueError as exc: return error(str(exc))
    sensor = db.session.get(Sensor, sensor_id)
    if not sensor: return error("Sensor tidak ditemukan.", 404)
    if not sensor.is_active: return error("Sensor sedang tidak aktif.", 409)
    api_key = request.headers.get("X-Device-Key", "")
    if not api_key or not sensor.device.verify_api_key(api_key):
        return error("API key perangkat tidak valid.", 401)
    reading = Reading(sensor_id=sensor.id, value=value, recorded_at=recorded_at)
    db.session.add(reading)
    sensor.device.last_seen_at = datetime.utcnow()
    sensor.device.status = "online"
    alert = None
    if sensor.min_threshold is not None and value < sensor.min_threshold:
        alert = Alert(device_id=sensor.device_id, sensor_id=sensor.id, alert_type="below_threshold",
                      message=f"{sensor.name} bernilai {value} {sensor.unit}, di bawah batas minimum {sensor.min_threshold}.", severity="warning")
    elif sensor.max_threshold is not None and value > sensor.max_threshold:
        alert = Alert(device_id=sensor.device_id, sensor_id=sensor.id, alert_type="above_threshold",
                      message=f"{sensor.name} bernilai {value} {sensor.unit}, melebihi batas maksimum {sensor.max_threshold}.", severity="critical")
    if alert: db.session.add(alert)
    db.session.commit()
    data = {"reading": reading.to_dict(), "alert": alert.to_dict() if alert else None}
    return success(data, "Telemetri berhasil disimpan.", 201)

@readings_bp.get("")
def list_readings():
    try:
        page = positive_int(request.args.get("page", 1), "page")
        per_page = positive_int(request.args.get("per_page", 20), "per_page")
        if per_page > 100: return error("per_page maksimal 100.")
    except ValueError as exc: return error(str(exc))
    query = Reading.query.join(Sensor)
    for key, column in (("sensor_id", Reading.sensor_id), ("device_id", Sensor.device_id)):
        if request.args.get(key):
            try: query = query.filter(column == int(request.args[key]))
            except ValueError: return error(f"{key} harus berupa integer.")
    for key, op in (("start", "start"), ("end", "end")):
        if request.args.get(key):
            try: dt = parse_datetime(request.args[key], key)
            except ValueError as exc: return error(str(exc))
            query = query.filter(Reading.recorded_at >= dt if op == "start" else Reading.recorded_at <= dt)
    sort = request.args.get("sort", "desc").lower()
    if sort not in {"asc", "desc"}: return error("sort harus asc atau desc.")
    query = query.order_by(asc(Reading.recorded_at) if sort == "asc" else desc(Reading.recorded_at))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return success([x.to_dict() for x in pagination.items], meta={"page": page, "per_page": per_page,
        "total": pagination.total, "pages": pagination.pages})

@readings_bp.get("/<int:reading_id>")
def get_reading(reading_id):
    row = db.session.get(Reading, reading_id)
    if not row: return error("Reading tidak ditemukan.", 404)
    return success(row.to_dict())
