from datetime import datetime
from flask import Blueprint, request
from ..extensions import db
from ..models import Alert
from ..utils import error, positive_int, success, iso

alerts_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")

@alerts_bp.get("")
def list_alerts():
    query = Alert.query
    for key in ("status", "severity"):
        if request.args.get(key): query = query.filter(getattr(Alert, key) == request.args[key])
    if request.args.get("device_id"):
        try: query = query.filter_by(device_id=positive_int(request.args["device_id"], "device_id"))
        except ValueError as exc: return error(str(exc))
    try:
        page = positive_int(request.args.get("page", 1), "page")
        per_page = positive_int(request.args.get("per_page", 20), "per_page")
        if per_page > 100: return error("per_page maksimal 100.")
    except ValueError as exc: return error(str(exc))
    pagination = query.order_by(Alert.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return success([x.to_dict() for x in pagination.items], meta={"page": page, "per_page": per_page,
        "total": pagination.total, "pages": pagination.pages})

@alerts_bp.get("/<int:alert_id>")
def get_alert(alert_id):
    row = db.session.get(Alert, alert_id)
    if not row: return error("Alert tidak ditemukan.", 404)
    return success(row.to_dict())

@alerts_bp.patch("/<int:alert_id>")
def update_alert(alert_id):
    row = db.session.get(Alert, alert_id)
    if not row: return error("Alert tidak ditemukan.", 404)
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict): return error("Body harus berupa JSON object.")
    status = payload.get("status")
    if status not in {"open", "acknowledged", "resolved"}:
        return error("status harus open, acknowledged, atau resolved.")
    row.status = status
    row.resolved_at = datetime.utcnow() if status == "resolved" else None
    db.session.commit()
    return success(row.to_dict(), "Status alert berhasil diperbarui.")
