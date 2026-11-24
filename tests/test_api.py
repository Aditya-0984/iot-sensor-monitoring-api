def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["data"]["status"] == "healthy"


def test_create_site(client):
    response = client.post("/api/sites", json={"name": "Gedung B", "location": "Sleman"})
    assert response.status_code == 201
    assert response.get_json()["data"]["name"] == "Gedung B"


def test_site_validation_error(client):
    response = client.post("/api/sites", json={"location": "Sleman"})
    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_create_sensor_threshold_validation(client):
    response = client.post("/api/sensors", json={"device_id": 1, "name": "Suhu", "sensor_type": "temperature",
        "unit": "C", "min_threshold": 35, "max_threshold": 20})
    assert response.status_code == 400


def test_ingest_reading_success(client):
    response = client.post("/api/readings", headers={"X-Device-Key": "test-api-key"},
                           json={"sensor_id": 1, "value": 25.5})
    assert response.status_code == 201
    assert response.get_json()["data"]["reading"]["value"] == 25.5
    assert response.get_json()["data"]["alert"] is None


def test_invalid_api_key(client):
    response = client.post("/api/readings", headers={"X-Device-Key": "wrong"},
                           json={"sensor_id": 1, "value": 25})
    assert response.status_code == 401


def test_non_numeric_reading(client):
    response = client.post("/api/readings", headers={"X-Device-Key": "test-api-key"},
                           json={"sensor_id": 1, "value": "panas"})
    assert response.status_code == 400


def test_threshold_creates_alert(client):
    response = client.post("/api/readings", headers={"X-Device-Key": "test-api-key"},
                           json={"sensor_id": 1, "value": 35})
    assert response.status_code == 201
    assert response.get_json()["data"]["alert"]["alert_type"] == "above_threshold"


def test_readings_pagination(client):
    for value in (21, 22, 23):
        client.post("/api/readings", headers={"X-Device-Key": "test-api-key"}, json={"sensor_id": 1, "value": value})
    response = client.get("/api/readings?page=1&per_page=2")
    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 2
    assert response.get_json()["meta"]["total"] == 3


def test_create_maintenance_log(client):
    response = client.post("/api/maintenance-logs", json={"device_id": 1, "technician": "Budi", "action": "Pemeriksaan sensor"})
    assert response.status_code == 201
    assert response.get_json()["data"]["technician"] == "Budi"


def test_alert_status_update(client):
    client.post("/api/readings", headers={"X-Device-Key": "test-api-key"}, json={"sensor_id": 1, "value": 35})
    response = client.get("/api/alerts")
    alert_id = response.get_json()["data"][0]["id"]
    updated = client.patch(f"/api/alerts/{alert_id}", json={"status": "resolved"})
    assert updated.status_code == 200
    assert updated.get_json()["data"]["status"] == "resolved"
