# Analisis Proyek: IoT Sensor Monitoring API

## 1. Latar belakang dan masalah
Lingkungan seperti ruang server, laboratorium, atau ruang penyimpanan perlu dipantau agar perubahan suhu dan kelembapan dapat diketahui. Pencatatan manual tidak selalu menghasilkan histori yang konsisten dan dapat terlambat diketahui ketika nilai sensor melewati batas yang ditentukan.

Proyek ini menyediakan REST API untuk menyimpan telemetri simulasi dari perangkat IoT, mengelola lokasi/perangkat/sensor, serta membuat alert otomatis berdasarkan ambang batas sensor.

## 2. Pengguna dan aktor
- **Pengelola fasilitas:** mendaftarkan lokasi, perangkat, dan sensor; melihat histori dan alert.
- **Perangkat IoT:** mengirim nilai sensor melalui endpoint telemetri dengan header API key.
- **Teknisi:** membuat catatan pemeliharaan dan memperbarui status alert.

## 3. Fitur utama MVP
1. CRUD lokasi (`sites`).
2. CRUD perangkat (`devices`) dengan kode perangkat unik dan penyimpanan API key dalam bentuk hash.
3. CRUD sensor (`sensors`) dengan unit serta batas minimum/maksimum.
4. Menerima dan melihat telemetri (`readings`), termasuk filter dan pagination.
5. Membuat alert saat nilai berada di luar ambang batas dan memperbarui status alert.
6. Mencatat dan melihat pemeliharaan perangkat (`maintenance_logs`).
7. Health check untuk memeriksa apakah API berjalan.

## 4. Alur data
1. Pengelola menambahkan site.
2. Pengelola mendaftarkan device pada site dan menentukan API key.
3. Sensor ditautkan ke device dengan unit dan threshold.
4. Device mengirim `sensor_id` dan `value` ke `POST /api/readings` dengan header `X-Device-Key`.
5. API memeriksa API key dan status sensor, lalu menyimpan reading.
6. Jika nilai kurang dari `min_threshold` atau melebihi `max_threshold`, API membuat alert.
7. Pengelola/teknisi memeriksa alert dan dapat mengubah status menjadi `acknowledged` atau `resolved`.

## 5. Aset, ancaman, dan mitigasi dasar
- **Aset:** data lokasi, identitas perangkat, konfigurasi threshold, histori telemetri, dan catatan alert/pemeliharaan.
- **Ancaman/risiko:** pengiriman telemetri tanpa izin, data tidak valid, duplikasi kode perangkat, dan paparan API key.
- **Mitigasi MVP:** hash API key saat disimpan, validasi input, unique constraint `device_code`, penggunaan HTTP status code konsisten, dan tidak mengembalikan API key pada response.
- **Catatan:** endpoint administrasi pada MVP ini belum memakai autentikasi admin/role. Aplikasi hanya untuk demo lokal dan tidak boleh dipublikasikan ke internet sebelum autentikasi, otorisasi, HTTPS, pengelolaan secret, dan pembatasan akses diterapkan.

## 6. Batasan sistem
- Data menggunakan simulasi; belum terhubung ke sensor fisik atau MQTT gateway.
- SQLite dipakai untuk pengembangan lokal.
- Belum ada akun pengguna, JWT, role-based access control, notifikasi eksternal, maupun dashboard frontend.
- Perangkat demo dan API key pada seed hanya untuk latihan lokal; ganti sebelum penggunaan nyata.

## 7. Rencana pengembangan UAS
1. Autentikasi JWT dan role admin/teknisi.
2. Dashboard frontend untuk grafik suhu/kelembapan.
3. Integrasi ESP32 atau broker MQTT pada lingkungan uji milik sendiri.
4. Notifikasi alert melalui kanal yang disetujui.
5. Optimasi query, indeks, ekspor laporan, dan retensi data.
6. Deployment HTTPS disertai logging, backup, dan manajemen secret.
