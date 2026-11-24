from flask import Blueprint, request
from ..extensions import db
from ..models import MaintenanceLog, Device
from ..utils import error, get_json_object, required_text, optional_text, positive_int, parse_datetime, success

maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/api/maintenance-logs")

@maintenance_bp.get("")
def list_logs():
    query = MaintenanceLog.query
    if request.args.get("device_id"):
        try: query = query.filter_by(device_id=positive_int(request.args["device_id"], "device_id"))
        except ValueError as exc: return error(str(exc))
    return success([x.to_dict() for x in query.order_by(MaintenanceLog.performed_at.desc()).all()])

@maintenance_bp.post("")
def create_log():
    payload = get_json_object()
    if payload is None: return error("Body harus berupa JSON object.")
    try:
        device_id = positive_int(payload.get("device_id"), "device_id")
        if not db.session.get(Device, device_id): return error("Device tidak ditemukan.", 404)
        row = MaintenanceLog(device_id=device_id, technician=required_text(payload, "technician"),
            action=required_text(payload, "action", 200), notes=optional_text(payload, "notes", 1000),
            performed_at=parse_datetime(payload.get("performed_at"), "performed_at"))
        db.session.add(row); db.session.commit()
        return success(row.to_dict(), "Log pemeliharaan berhasil dibuat.", 201)
    except ValueError as exc: return error(str(exc))

@maintenance_bp.get("/<int:log_id>")
def get_log(log_id):
    row = db.session.get(MaintenanceLog, log_id)
    if not row: return error("Log pemeliharaan tidak ditemukan.", 404)
    return success(row.to_dict())
