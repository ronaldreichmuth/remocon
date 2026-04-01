# Heizung – Hot Water Temperature Logger

Reads the hot water temperature every 5 minutes from [remocon-net.remotethermo.com](https://www.remocon-net.remotethermo.com) and displays the last 3 days in a browser chart.

## Requirements

- Docker & Docker Compose (e.g. Synology NAS with Container Manager)
- Login credentials for remocon-net.remotethermo.com
- Gateway ID (visible in the web interface after login)

## Setup

```bash
git clone https://github.com/ronaldreichmuth/remocon.git
cd remocon
cp .env.example .env
```

Edit `.env` and fill in your credentials:
```
EMAIL=your@email.com
PASSWORD=your_password
GATEWAY_ID=your_gateway_id
```

## Start

```bash
sudo docker-compose up -d
```

Web interface: **http://nas-ip:5000**

## Stop

```bash
sudo docker-compose down
```

## Data

The SQLite database is stored in the Docker volume `heizung_data` and persists across updates.
