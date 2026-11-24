import pytest
from app import create_app
from app.extensions import db
from app.models import Site, Device, Sensor

@pytest.fixture()
def app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://", "SECRET_KEY": "test-secret"})
    with app.app_context():
        db.create_all()
        site = Site(name="Lab Test", location="Yogyakarta")
        db.session.add(site); db.session.flush()
        device = Device(site_id=site.id, name="Device Test", device_code="TEST-001", status="offline")
        device.set_api_key("test-api-key")
        db.session.add(device); db.session.flush()
        sensor = Sensor(device_id=device.id, name="Suhu", sensor_type="temperature", unit="°C",
                        min_threshold=18, max_threshold=30, is_active=True)
        db.session.add(sensor); db.session.commit()
    yield app
    with app.app_context():
        db.session.remove(); db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()
