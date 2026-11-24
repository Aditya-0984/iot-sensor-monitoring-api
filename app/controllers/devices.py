from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from ..extensions import db
from ..models import Device, Site
from ..utils import error, get_json_object, required_text, optional_text, success

devices_bp = Blueprint("devices", __name__, url_prefix="/api/devices")
VALID_STATUS = {"online", "offline", "maintenance"}

@devices_bp.get("")
def list_devices():
    query = Device.query
    if request.args.get("site_id"):
        try: query = query.filter_by(site_id=int(request.args["site_id"]))
        except ValueError: return error("site_id harus berupa integer.")
    rows = query.order_by(Device.id.asc()).all()
    return success([row.to_dict() for row in rows])

@devices_bp.post("")
def create_device():
    payload = get_json_object()
    if payload is None: return error("Body harus berupa JSON object.")
    try:
        site_id = int(payload.get("site_id"))
        if site_id < 1: raise ValueError
    except (TypeError, ValueError): return error("'site_id' harus berupa integer positif.")
    if not db.session.get(Site, site_id): return error("Site tidak ditemukan.", 404)
    try:
        api_key = required_text(payload, "api_key", 255)
        status = payload.get("status", "offline")
        if status not in VALID_STATUS: return error("status harus online, offline, atau maintenance.")
        device = Device(site_id=site_id, name=required_text(payload, "name"),
                        device_code=required_text(payload, "device_code", 80), status=status)
        device.set_api_key(api_key)
        db.session.add(device); db.session.commit()
        return success(device.to_dict(), "Device berhasil didaftarkan. Simpan API key di sisi perangkat.", 201)
    except ValueError as exc: return error(str(exc))
    except IntegrityError:
        db.session.rollback(); return error("device_code sudah digunakan.", 409)

@devices_bp.get("/<int:device_id>")
def get_device(device_id):
    row = db.session.get(Device, device_id)
    if not row: return error("Device tidak ditemukan.", 404)
    return success(row.to_dict())

@devices_bp.put("/<int:device_id>")
def update_device(device_id):
    row = db.session.get(Device, device_id)
    if not row: return error("Device tidak ditemukan.", 404)
    payload = get_json_object()
    if payload is None: return error("Body harus berupa JSON object.")
    try:
        if "site_id" in payload:
            try: site_id = int(payload["site_id"])
            except (TypeError, ValueError): return error("site_id harus integer.")
            if not db.session.get(Site, site_id): return error("Site tidak ditemukan.", 404)
            row.site_id = site_id
        if "name" in payload: row.name = required_text(payload, "name")
        if "status" in payload:
            if payload["status"] not in VALID_STATUS: return error("status tidak valid.")
            row.status = payload["status"]
        if "api_key" in payload: row.set_api_key(required_text(payload, "api_key", 255))
        db.session.commit(); return success(row.to_dict(), "Device berhasil diperbarui.")
    except ValueError as exc: db.session.rollback(); return error(str(exc))

@devices_bp.delete("/<int:device_id>")
def delete_device(device_id):
    row = db.session.get(Device, device_id)
    if not row: return error("Device tidak ditemukan.", 404)
    db.session.delete(row); db.session.commit()
    return success({"id": device_id}, "Device berhasil dihapus.")
