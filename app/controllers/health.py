from flask import Blueprint
from ..utils import success

health_bp = Blueprint("health", __name__)

@health_bp.get("/api/health")
def health():
    return success({"status": "healthy"}, "API aktif")
