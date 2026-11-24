# Entity Relationship Diagram (ERD)

Diagram berikut dapat dirender oleh GitHub Markdown yang mendukung Mermaid.

```mermaid
erDiagram
    SITES ||--o{ DEVICES : hosts
    DEVICES ||--o{ SENSORS : has
    SENSORS ||--o{ READINGS : produces
    DEVICES ||--o{ ALERTS : raises
    SENSORS ||--o{ ALERTS : relates_to
    DEVICES ||--o{ MAINTENANCE_LOGS : receives

    SITES {
        int id PK
        string name
        string location
        string description
        datetime created_at
    }
    DEVICES {
        int id PK
        int site_id FK
        string name
        string device_code UK
        string status
        string api_key_hash
        datetime last_seen_at
        datetime created_at
    }
    SENSORS {
        int id PK
        int device_id FK
        string name
        string sensor_type
        string unit
        float min_threshold
        float max_threshold
        boolean is_active
        datetime created_at
    }
    READINGS {
        int id PK
        int sensor_id FK
        float value
        datetime recorded_at
        datetime created_at
    }
    ALERTS {
        int id PK
        int device_id FK
        int sensor_id FK
        string alert_type
        string message
        string severity
        string status
        datetime created_at
        datetime resolved_at
    }
    MAINTENANCE_LOGS {
        int id PK
        int device_id FK
        string technician
        string action
        string notes
        datetime performed_at
        datetime created_at
    }
```

## Ringkasan relasi

- `sites` 1:N `devices`: satu lokasi dapat memiliki banyak perangkat.
- `devices` 1:N `sensors`: satu perangkat dapat memiliki beberapa sensor.
- `sensors` 1:N `readings`: satu sensor menghasilkan banyak data telemetri.
- `devices` 1:N `alerts`: satu perangkat dapat menghasilkan banyak alert.
- `sensors` 1:N `alerts`: alert dapat terkait dengan sensor tertentu; `sensor_id` dapat kosong untuk alert tingkat perangkat.
- `devices` 1:N `maintenance_logs`: riwayat pemeliharaan disimpan per perangkat.

Semua tabel menggunakan `id` sebagai primary key. Kolom berakhiran `_id` yang merujuk tabel lain adalah foreign key. `devices.device_code` memiliki unique constraint.
