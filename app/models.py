from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
from .utils import iso, utc_now


class Site(db.Model):
    __tablename__ = "sites"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    devices = db.relationship("Device", back_populates="site", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "location": self.location,
                "description": self.description, "created_at": iso(self.created_at)}


class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    device_code = db.Column(db.String(80), nullable=False, unique=True, index=True)
    status = db.Column(db.String(20), nullable=False, default="offline")
    api_key_hash = db.Column(db.String(255), nullable=False)
    last_seen_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    site = db.relationship("Site", back_populates="devices")
    sensors = db.relationship("Sensor", back_populates="device", cascade="all, delete-orphan")
    alerts = db.relationship("Alert", back_populates="device", cascade="all, delete-orphan")
    maintenance_logs = db.relationship("MaintenanceLog", back_populates="device", cascade="all, delete-orphan")

    def set_api_key(self, raw_key):
        self.api_key_hash = generate_password_hash(raw_key)

    def verify_api_key(self, raw_key):
        return check_password_hash(self.api_key_hash, raw_key or "")

    def to_dict(self):
        return {"id": self.id, "site_id": self.site_id, "name": self.name,
                "device_code": self.device_code, "status": self.status,
                "last_seen_at": iso(self.last_seen_at), "created_at": iso(self.created_at)}


class Sensor(db.Model):
    __tablename__ = "sensors"
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    sensor_type = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    min_threshold = db.Column(db.Float)
    max_threshold = db.Column(db.Float)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    device = db.relationship("Device", back_populates="sensors")
    readings = db.relationship("Reading", back_populates="sensor", cascade="all, delete-orphan")
    alerts = db.relationship("Alert", back_populates="sensor")

    def to_dict(self):
        return {"id": self.id, "device_id": self.device_id, "name": self.name,
                "sensor_type": self.sensor_type, "unit": self.unit,
                "min_threshold": self.min_threshold, "max_threshold": self.max_threshold,
                "is_active": self.is_active, "created_at": iso(self.created_at)}


class Reading(db.Model):
    __tablename__ = "readings"
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False, index=True)
    value = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, nullable=False, default=utc_now, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    sensor = db.relationship("Sensor", back_populates="readings")

    def to_dict(self):
        return {"id": self.id, "sensor_id": self.sensor_id, "value": self.value,
                "unit": self.sensor.unit if self.sensor else None,
                "recorded_at": iso(self.recorded_at), "created_at": iso(self.created_at)}


class Alert(db.Model):
    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensors.id", ondelete="SET NULL"), nullable=True, index=True)
    alert_type = db.Column(db.String(40), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    severity = db.Column(db.String(20), nullable=False, default="warning")
    status = db.Column(db.String(20), nullable=False, default="open", index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    resolved_at = db.Column(db.DateTime)
    device = db.relationship("Device", back_populates="alerts")
    sensor = db.relationship("Sensor", back_populates="alerts")

    def to_dict(self):
        return {"id": self.id, "device_id": self.device_id, "sensor_id": self.sensor_id,
                "alert_type": self.alert_type, "message": self.message,
                "severity": self.severity, "status": self.status,
                "created_at": iso(self.created_at), "resolved_at": iso(self.resolved_at)}


class MaintenanceLog(db.Model):
    __tablename__ = "maintenance_logs"
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    technician = db.Column(db.String(120), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.String(1000))
    performed_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    device = db.relationship("Device", back_populates="maintenance_logs")

    def to_dict(self):
        return {"id": self.id, "device_id": self.device_id, "technician": self.technician,
                "action": self.action, "notes": self.notes,
                "performed_at": iso(self.performed_at), "created_at": iso(self.created_at)}
