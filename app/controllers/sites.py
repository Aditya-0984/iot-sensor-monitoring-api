from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from ..extensions import db
from ..models import Site
from ..utils import error, get_json_object, required_text, optional_text, success

sites_bp = Blueprint("sites", __name__, url_prefix="/api/sites")

@sites_bp.get("")
def list_sites():
    rows = Site.query.order_by(Site.id.asc()).all()
    return success([row.to_dict() for row in rows])

@sites_bp.post("")
def create_site():
    payload = get_json_object()
    if payload is None: return error("Body harus berupa JSON object.")
    try:
        site = Site(name=required_text(payload, "name"), location=required_text(payload, "location", 200),
                    description=optional_text(payload, "description"))
        db.session.add(site); db.session.commit()
        return success(site.to_dict(), "Site berhasil dibuat.", 201)
    except ValueError as exc: return error(str(exc))

@sites_bp.get("/<int:site_id>")
def get_site(site_id):
    site = db.session.get(Site, site_id)
    if not site: return error("Site tidak ditemukan.", 404)
    return success(site.to_dict())

@sites_bp.put("/<int:site_id>")
def update_site(site_id):
    site = db.session.get(Site, site_id)
    if not site: return error("Site tidak ditemukan.", 404)
    payload = get_json_object()
    if payload is None: return error("Body harus berupa JSON object.")
    try:
        if "name" in payload: site.name = required_text(payload, "name")
        if "location" in payload: site.location = required_text(payload, "location", 200)
        if "description" in payload: site.description = optional_text(payload, "description")
        db.session.commit(); return success(site.to_dict(), "Site berhasil diperbarui.")
    except ValueError as exc: db.session.rollback(); return error(str(exc))

@sites_bp.delete("/<int:site_id>")
def delete_site(site_id):
    site = db.session.get(Site, site_id)
    if not site: return error("Site tidak ditemukan.", 404)
    db.session.delete(site); db.session.commit()
    return success({"id": site_id}, "Site berhasil dihapus beserta data turunannya.")
