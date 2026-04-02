"""
Liest die Warmwassertemperatur alle 5 Minuten von remocon-net.remotethermo.com
und speichert die Werte in einer SQLite-Datenbank.
"""

import os
import sqlite3
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://www.remocon-net.remotethermo.com"
EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]
GATEWAY_ID = os.environ["GATEWAY_ID"]
INTERVAL_SECONDS = 5 * 60
DB_FILE = os.environ.get("DB_FILE", "/data/heizung.db")


def login(session: requests.Session) -> bool:
    url = f"{BASE_URL}/R2/Account/Login"
    session.cookies.set("browserUtcOffset", "-60")
    resp = session.post(
        url,
        data={"Email": EMAIL, "Password": PASSWORD, "RememberMe": "false"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    resp.raise_for_status()
    result = resp.json()
    return result.get("ok", False)


def get_plant_data(session: requests.Session):
    url = f"{BASE_URL}/R2/PlantHomeBsb/GetData/{GATEWAY_ID}"
    resp = session.post(
        url,
        json={"useCache": True, "zone": 1, "filter": {"progIds": "null", "plant": True, "zone": True}},
        timeout=30,
    )
    resp.raise_for_status()
    plant = resp.json().get("data", {}).get("plantData", {})
    return plant.get("dhwStorageTemp"), plant.get("outsideTemp"), plant.get("heatPumpOn")


def init_db():
    con = sqlite3.connect(DB_FILE)
    con.execute("""
        CREATE TABLE IF NOT EXISTS warmwasser (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp     TEXT NOT NULL,
            temp_c        REAL NOT NULL,
            outside_temp  REAL
        )
    """)
    for col in ["outside_temp REAL", "heat_pump_on INTEGER"]:
        try:
            con.execute(f"ALTER TABLE warmwasser ADD COLUMN {col}")
        except Exception:
            pass
    con.commit()
    con.close()


def insert_db(timestamp: str, temp: float, outside_temp, heat_pump_on):
    con = sqlite3.connect(DB_FILE)
    con.execute(
        "INSERT INTO warmwasser (timestamp, temp_c, outside_temp, heat_pump_on) VALUES (?, ?, ?, ?)",
        (timestamp, temp, outside_temp, int(heat_pump_on) if heat_pump_on is not None else None),
    )
    con.commit()
    con.close()


def run():
    init_db()
    session = requests.Session()

    print("Einloggen...")
    if not login(session):
        raise RuntimeError("Login fehlgeschlagen. Bitte Zugangsdaten prüfen.")
    print("Login erfolgreich.")

    while True:
        try:
            temp, outside, pump = get_plant_data(session)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if temp is not None:
                outside_str = f"  Aussen: {outside:.1f} °C" if outside is not None else ""
                pump_str = f"  Wärmepumpe: {'AN' if pump else 'AUS'}" if pump is not None else ""
                print(f"{timestamp}  Warmwasser: {temp:.1f} °C{outside_str}{pump_str}")
                insert_db(timestamp, temp, outside, pump)
            else:
                print(f"{timestamp}  Temperatur nicht verfügbar (kein dhwStorageTemp in Antwort)")

        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code in (401, 403):
                print("Session abgelaufen, neu einloggen...")
                if not login(session):
                    print("Re-Login fehlgeschlagen, nächster Versuch in 60s")
                    time.sleep(60)
                    continue
            else:
                print(f"HTTP-Fehler: {e}")

        except Exception as e:
            print(f"Fehler: {e}")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
