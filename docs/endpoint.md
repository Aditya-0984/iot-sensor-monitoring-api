# Ringkasan Endpoint

Format response umum:

```json
{
  "success": true,
  "message": "OK",
  "data": {}
}
```

Error memakai bentuk konsisten: `success: false`, `message`, dan `error.code` (serta `error.details` bila ada).

| Method | Endpoint | Keterangan | Status umum |
|---|---|---|---|
| GET | `/api/health` | Cek status API | 200 |
| GET, POST | `/api/sites` | Daftar/tambah lokasi | 200, 201, 400 |
| GET, PUT, DELETE | `/api/sites/{site_id}` | Detail/ubah/hapus lokasi | 200, 400, 404 |
| GET, POST | `/api/devices` | Daftar/registrasi perangkat | 200, 201, 400, 404, 409 |
| GET, PUT, DELETE | `/api/devices/{device_id}` | Detail/ubah/hapus perangkat | 200, 400, 404 |
| GET, POST | `/api/sensors` | Daftar/registrasi sensor | 200, 201, 400, 404 |
| GET, PUT, DELETE | `/api/sensors/{sensor_id}` | Detail/ubah/hapus sensor | 200, 400, 404 |
| GET, POST | `/api/readings` | Histori/ingest telemetri | 200, 201, 400, 401, 404, 409 |
| GET | `/api/readings/{reading_id}` | Detail telemetri | 200, 404 |
| GET | `/api/alerts` | Daftar/filter alert | 200, 400 |
| GET, PATCH | `/api/alerts/{alert_id}` | Detail/ubah status alert | 200, 400, 404 |
| GET, POST | `/api/maintenance-logs` | Daftar/tambah log pemeliharaan | 200, 201, 400, 404 |
| GET | `/api/maintenance-logs/{log_id}` | Detail log pemeliharaan | 200, 404 |

## Request utama

### Buat site — `POST /api/sites`

```json
{"name":"Gedung A","location":"Yogyakarta","description":"Ruang server"}
```

### Daftarkan device — `POST /api/devices`

```json
{"site_id":1,"name":"ESP32 Ruang Server","device_code":"ESP32-001","api_key":"ganti-dengan-kunci-demo","status":"offline"}
```

API key di-hash sebelum disimpan dan tidak dikembalikan pada response.

### Daftarkan sensor — `POST /api/sensors`

```json
{"device_id":1,"name":"Sensor Suhu","sensor_type":"temperature","unit":"°C","min_threshold":18,"max_threshold":30}
```

### Kirim telemetri — `POST /api/readings`

Header: `X-Device-Key: demo-iot-key-123`

```json
{"sensor_id":1,"value":35}
```

Nilai `35` melampaui batas maksimum sensor suhu pada seed, sehingga response menyertakan alert otomatis.

### Filter/pagination telemetri

`GET /api/readings?page=1&per_page=10&sort=desc&sensor_id=1`

Query yang tersedia: `page`, `per_page` (maksimal 100), `sort` (`asc`/`desc`), `sensor_id`, `device_id`, `start`, dan `end`.

### Ubah status alert — `PATCH /api/alerts/1`

```json
{"status":"resolved"}
```

Status yang diizinkan: `open`, `acknowledged`, `resolved`.
