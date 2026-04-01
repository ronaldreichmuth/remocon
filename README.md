# Heizung – Warmwasser Temperaturlogger

Liest alle 5 Minuten die Warmwassertemperatur von [remocon-net.remotethermo.com](https://www.remocon-net.remotethermo.com) und zeigt den Verlauf der letzten 3 Tage im Browser.

## Voraussetzungen

- Docker & Docker Compose (z.B. Synology NAS mit Container Manager)
- Zugangsdaten für remocon-net.remotethermo.com
- Gateway ID (sichtbar im Web-Interface nach dem Login)

## Installation

```bash
git clone https://github.com/ronaldreichmuth/remocon.git
cd remocon
cp .env.example .env
```

`.env` öffnen und Zugangsdaten eintragen:
```
EMAIL=deine@email.ch
PASSWORD=dein_passwort
GATEWAY_ID=deine_gateway_id
```

## Starten

```bash
sudo docker-compose up -d
```

Webinterface: **http://nas-ip:5000**

## Stoppen

```bash
sudo docker-compose down
```

## Daten

Die SQLite-Datenbank wird im Docker-Volume `heizung_data` gespeichert und bleibt bei Updates erhalten.
