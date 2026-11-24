# IoT Sensor Monitoring API

MVP REST API untuk pemantauan telemetri suhu dan kelembapan menggunakan Python Flask, Flask-SQLAlchemy (ORM), SQLite, dan pemisahan controller/model bergaya MVC.

## 1. Masalah, pengguna, dan batasan
API membantu pengelola fasilitas memantau pembacaan sensor simulasi di lokasi seperti ruang server atau laboratorium. Pengelola mengelola site, device, dan sensor; perangkat mengirim telemetri; teknisi melihat alert dan mencatat pemeliharaan. Rincian analisis ada di `docs/analisis_proyek.md`.

Data bersifat simulasi dan belum terhubung ke perangkat fisik/MQTT. SQLite digunakan untuk pengembangan lokal. Endpoint administrasi MVP belum memiliki autentikasi admin, sehingga aplikasi hanya untuk demo lokal. Jangan deploy ke internet sebelum menambahkan autentikasi/otorisasi, HTTPS, pengelolaan secret, dan kontrol akses.

## 2. Struktur proyek

```text
app/
  controllers/       # blueprint/controller per resource
  extensions.py      # SQLAlchemy dan Flask-Migrate
  models.py          # enam model/tabel ORM
  utils.py           # validasi dan format response
  __init__.py        # application factory
config.py
run.py
seed.py
requirements.txt
instance/            # database SQLite lokal
 tests/              # automated test
 docs/               # ERD, analisis, daftar endpoint
 postman/            # koleksi Postman
 openapi.yaml
```

## 3. Persiapan Windows PowerShell

Buka folder proyek di VS Code. Periksa Python:

```powershell
python --version
```

Buat dan aktifkan virtual environment (cukup sekali untuk pembuatan; aktivasi dilakukan setiap membuka terminal baru):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Jika PowerShell memblokir aktivasi pada terminal saat ini:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Pasang dependency:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

File `.env` bersifat opsional. Untuk menyalinnya:

```powershell
Copy-Item .env.example .env
```

## 4. Membuat database dan seed data

```powershell
python seed.py
```

Perintah tersebut membuat tabel yang diperlukan dan memasukkan data simulasi jika belum tersedia. Seed demo:
- Site: `Gedung A`
- Device: `ESP32-DEMO-001`
- Sensor ID 1: suhu, unit °C, threshold 18–30
- Sensor ID 2: kelembapan, unit %, threshold 30–70
- API key demo lokal: `demo-iot-key-123`

API key tersebut hanya untuk latihan lokal. Jangan gunakan sebagai secret produksi.

## 5. Menjalankan API

```powershell
python run.py
```

Cek `GET http://127.0.0.1:5000/api/health`. API berjalan pada `http://127.0.0.1:5000`.

## 6. Contoh kirim telemetri

Di terminal PowerShell lain atau Postman, kirim:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/api/readings `
  -Headers @{"X-Device-Key"="demo-iot-key-123"} `
  -ContentType "application/json" `
  -Body '{"sensor_id":1,"value":27.5}'
```

Nilai `27.5` berada di rentang suhu 18–30 °C. Untuk menguji alert, kirim nilai `35`; API menyimpan reading dan membuat alert `above_threshold`.

## 7. Endpoint dan dokumentasi

Daftar endpoint, request utama, response, filter, dan status code ada di `docs/endpoint.md`. Spesifikasi OpenAPI tersedia di `openapi.yaml`, sedangkan koleksi pengujian manual ada di `postman/IoT-Sensor-Monitoring.postman_collection.json`.

Fitur filter/pagination antara lain:

`GET /api/readings?page=1&per_page=10&sort=desc&sensor_id=1`

## 8. Automated test

Pastikan virtual environment aktif, lalu jalankan:

```powershell
python -m pytest -v
```

Test mencakup health check, pembuatan site, validasi input, validasi threshold, ingest telemetri berhasil, API key salah, nilai non-numerik, alert otomatis, pagination, pencatatan pemeliharaan, dan perubahan status alert.

## 9. Migration database

`python seed.py` menggunakan `db.create_all()` untuk inisialisasi lokal. Untuk mengelola migration dengan Flask-Migrate, jalankan satu kali:

```powershell
flask --app run.py db init
flask --app run.py db migrate -m "initial schema"
flask --app run.py db upgrade
```

Setelah model berubah, jalankan `flask --app run.py db migrate -m "deskripsi perubahan"` lalu `flask --app run.py db upgrade`.

## 10. ERD dan tabel

1. `sites`: lokasi pemasangan perangkat.
2. `devices`: perangkat IoT pada suatu site, termasuk hash API key.
3. `sensors`: sensor milik perangkat beserta unit dan threshold.
4. `readings`: histori pembacaan sensor.
5. `alerts`: peringatan otomatis saat threshold terlampaui.
6. `maintenance_logs`: catatan pemeliharaan perangkat.

ERD Mermaid ada di `docs/erd.md`.

## 11. Rencana pengembangan UAS

1. JWT dan role admin/teknisi.
2. Dashboard grafik telemetri.
3. Integrasi ESP32 atau simulator MQTT pada jaringan/lab milik sendiri.
4. Notifikasi alert.
5. Optimasi query, indeks, retensi data, dan ekspor laporan.
6. Deployment HTTPS, logging, backup, serta secret management.

## 12. Referensi

- Flask: https://flask.palletsprojects.com/
- Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/
- Flask-Migrate: https://flask-migrate.readthedocs.io/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Pytest: https://docs.pytest.org/
