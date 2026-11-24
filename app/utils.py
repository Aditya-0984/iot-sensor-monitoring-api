from datetime import datetime, timezone
from flask import jsonify


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def iso(value):
    return value.isoformat(timespec="seconds") + "Z" if value else None


def success(data=None, message="OK", status=200, meta=None):
    body = {"success": True, "message": message, "data": data}
    if meta is not None:
        body["meta"] = meta
    return jsonify(body), status


def error(message, status=400, details=None):
    body = {"success": False, "message": message, "error": {"code": status}}
    if details is not None:
        body["error"]["details"] = details
    return jsonify(body), status


def get_json_object():
    from flask import request
    if not request.is_json:
        return None
    payload = request.get_json(silent=True)
    return payload if isinstance(payload, dict) else None


def required_text(payload, field, max_length=120):
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{field}' wajib diisi sebagai teks.")
    value = value.strip()
    if len(value) > max_length:
        raise ValueError(f"'{field}' maksimal {max_length} karakter.")
    return value


def optional_text(payload, field, max_length=500):
    value = payload.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"'{field}' harus berupa teks.")
    value = value.strip()
    if len(value) > max_length:
        raise ValueError(f"'{field}' maksimal {max_length} karakter.")
    return value or None


def positive_int(value, field):
    if isinstance(value, bool):
        raise ValueError(f"'{field}' harus berupa bilangan bulat positif.")
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"'{field}' harus berupa bilangan bulat positif.")
    if parsed < 1:
        raise ValueError(f"'{field}' harus lebih besar dari 0.")
    return parsed


def numeric_value(value, field="value"):
    if isinstance(value, bool):
        raise ValueError(f"'{field}' harus berupa angka.")
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"'{field}' harus berupa angka.")
    if parsed != parsed or parsed in (float("inf"), float("-inf")):
        raise ValueError(f"'{field}' harus berupa angka yang valid.")
    return parsed


def parse_datetime(value, field="recorded_at"):
    if value is None:
        return utc_now()
    if not isinstance(value, str):
        raise ValueError(f"'{field}' harus berupa ISO-8601 datetime.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except ValueError:
        raise ValueError(f"'{field}' harus berupa ISO-8601 datetime.")
