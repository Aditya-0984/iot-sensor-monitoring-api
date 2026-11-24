from app import create_app
from app.extensions import db
from app.models import Site, Device, Sensor

DEMO_API_KEY = "demo-iot-key-123"
app = create_app()

with app.app_context():
    db.create_all()
    site = Site.query.filter_by(name="Gedung A").first()
    if site is None:
        site = Site(name="Gedung A", location="Yogyakarta", description="Lokasi simulasi pemantauan lingkungan")
        db.session.add(site)
        db.session.flush()

    device = Device.query.filter_by(device_code="ESP32-DEMO-001").first()
    if device is None:
        device = Device(site_id=site.id, name="ESP32 Ruang Server", device_code="ESP32-DEMO-001", status="offline")
        device.set_api_key(DEMO_API_KEY)
        db.session.add(device)
        db.session.flush()

    if not Sensor.query.filter_by(device_id=device.id, name="Sensor Suhu").first():
        db.session.add(Sensor(device_id=device.id, name="Sensor Suhu", sensor_type="temperature", unit="°C",
                              min_threshold=18.0, max_threshold=30.0, is_active=True))
    if not Sensor.query.filter_by(device_id=device.id, name="Sensor Kelembapan").first():
        db.session.add(Sensor(device_id=device.id, name="Sensor Kelembapan", sensor_type="humidity", unit="%",
                              min_threshold=30.0, max_threshold=70.0, is_active=True))
    db.session.commit()
    print("Seed selesai. Database siap digunakan.")
    print("Demo API key (lokal saja):", DEMO_API_KEY)
