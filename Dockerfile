FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY heizung.py web.py start.sh ./

RUN chmod +x start.sh

VOLUME ["/data"]

EXPOSE 5005

CMD ["./start.sh"]
