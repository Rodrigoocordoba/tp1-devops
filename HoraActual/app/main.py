from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import os

load_dotenv()

DEFAULT_TZ = os.getenv("DEFAULT_TZ", "UTC")

app = FastAPI(title="Now API", version="1.0.0")

def now_dt(tz_name: str):
    """Devuelve (dt_local, tz_name) validando la zona."""
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Timezone inválida. Usa formato IANA (ej: America/Argentina/Buenos_Aires, Europe/Madrid, UTC).",
        )
    dt_utc = datetime.now(timezone.utc)
    return dt_utc.astimezone(tz), tz_name

def pretty_place(tz_name: str) -> str:
    """
    Convierte 'America/Argentina/Buenos_Aires' -> 'Buenos Aires'
    (usa el último segmento, reemplazando '_' por ' ')
    Si solo viene 'UTC', devuelve 'UTC'.
    """
    parts = tz_name.split("/")
    last = parts[-1] if parts else tz_name
    return last.replace("_", " ")

@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})

@app.get("/now", response_class=PlainTextResponse)
def get_now(tz: str = Query(None, description="Zona IANA. Ej: America/Argentina/Buenos_Aires")):
    """
    Devuelve texto plano con el formato: 'lugar:hora'
    Ej: 'Buenos Aires: 13:27:05'
    """
    tz_name = tz or DEFAULT_TZ
    dt_loc, tz_name = now_dt(tz_name)
    place = pretty_place(tz_name)
    hhmmss = dt_loc.strftime("%H:%M:%S")
    return f"{place}: {hhmmss}"

@app.get("/now/json")
def get_now_json(tz: str = Query(None, description="Zona IANA")):
    """Versión JSON detallada (por si la necesitás)."""
    tz_name = tz or DEFAULT_TZ
    dt_loc, _ = now_dt(tz_name)
    dt_utc = dt_loc.astimezone(timezone.utc)
    return {
        "timezone": tz_name,
        "place": pretty_place(tz_name),
        "iso": dt_loc.isoformat(),
        "date": dt_loc.strftime("%Y-%m-%d"),
        "time": dt_loc.strftime("%H:%M:%S"),
        "offset": dt_loc.strftime("%z"),
        "epoch_ms": int(dt_loc.timestamp() * 1000),
        "utc_iso": dt_utc.isoformat(),
    }
