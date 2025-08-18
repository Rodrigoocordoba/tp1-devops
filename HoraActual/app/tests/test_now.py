# tests/test_now.py
import os
import re
import importlib
from fastapi.testclient import TestClient

def make_client(default_tz="UTC"):
    """
    Crea un TestClient asegurando DEFAULT_TZ para que las pruebas sean deterministas.
    Fuerza a recargar el módulo 'app.main' así toma la env al importar.
    """
    os.environ["DEFAULT_TZ"] = default_tz
    import app.main as main
    importlib.reload(main)
    return TestClient(main.app), main

def test_health_ok():
    client, _ = make_client()
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_now_plain_uses_default_tz_from_env():
    client, _ = make_client("UTC")
    r = client.get("/now")
    assert r.status_code == 200
    # Debe ser "UTC: HH:MM:SS"
    assert r.text.startswith("UTC:")
    assert re.match(r"^[\w .+\-]+: \d{2}:\d{2}:\d{2}$", r.text)

def test_now_plain_with_param_madrid():
    client, _ = make_client("UTC")
    r = client.get("/now", params={"tz": "Europe/Madrid"})
    assert r.status_code == 200
    # pretty_place("Europe/Madrid") -> "Madrid"
    assert r.text.startswith("Madrid:")
    assert re.match(r"^Madrid: \d{2}:\d{2}:\d{2}$", r.text)

def test_now_json_structure_and_invalid_tz():
    client, _ = make_client("UTC")
    # Estructura válida
    r_ok = client.get("/now/json", params={"tz": "UTC"})
    assert r_ok.status_code == 200
    body = r_ok.json()
    for key in ["timezone", "place", "iso", "date", "time", "offset", "epoch_ms", "utc_iso"]:
        assert key in body

    # Zona inválida -> 400
    r_bad = client.get("/now/json", params={"tz": "Not/AZone"})
    assert r_bad.status_code == 400
