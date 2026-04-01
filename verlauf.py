"""
Zeigt den Temperaturverlauf der letzten 3 Tage als Diagramm.
"""

import sqlite3
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DB_FILE = "heizung.db"


def load_data():
    seit = datetime.now() - timedelta(days=3)
    con = sqlite3.connect(DB_FILE)
    rows = con.execute(
        "SELECT timestamp, temp_c FROM warmwasser WHERE timestamp >= ? ORDER BY timestamp",
        (seit.strftime("%Y-%m-%d %H:%M:%S"),),
    ).fetchall()
    con.close()
    return rows


def plot(rows):
    if not rows:
        print("Keine Daten für die letzten 3 Tage vorhanden.")
        return

    timestamps = [datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S") for r in rows]
    temps = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(timestamps, temps, color="#e05a2b", linewidth=1.5)
    ax.fill_between(timestamps, temps, alpha=0.15, color="#e05a2b")

    ax.set_title("Warmwassertemperatur – letzte 3 Tage", fontsize=14)
    ax.set_ylabel("Temperatur (°C)")
    ax.set_xlabel("Zeit")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m %H:%M"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()
    ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot(load_data())
