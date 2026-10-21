"""
github_service.py
Kleiner lokaler Dienst, den n8n (im Docker-Container) aufruft.
Startet github_traffic.py höchstens einmal pro Tag und gibt die Kurzausgabe zurück.
n8n darf stündlich anfragen: Ist heute schon gelaufen, passiert nichts.

Start (im Ordner github_traffic):
  uvicorn github_service:app --host 172.17.0.1 --port 8766
"""

import os
import subprocess
import sys
import threading
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException

# Arbeitsordner = Projektordner (dort liegen .env, Skript, CSVs, Excel)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

API_KEY = os.getenv("SERVICE_API_KEY")
LAST_RUN = Path("last_run.txt")  # Datum des letzten erfolgreichen Laufs
lock = threading.Lock()          # nie zwei Läufe gleichzeitig
app = FastAPI(title="GitHub Traffic")


def auth(key):
    if not API_KEY or key != API_KEY:
        raise HTTPException(status_code=401, detail="falscher oder fehlender Schlüssel")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/run")
def run(x_api_key: str = Header(None)):
    auth(x_api_key)
    if not lock.acquire(blocking=False):
        return {"status": "läuft bereits", "ausgabe": ""}
    try:
        today = date.today().isoformat()
        if LAST_RUN.exists() and LAST_RUN.read_text().strip() == today:
            return {"status": "heute schon erledigt", "ausgabe": ""}
        r = subprocess.run([sys.executable, "github_traffic.py"],
                           capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            raise HTTPException(status_code=500, detail=r.stderr[-1000:])
        LAST_RUN.write_text(today)
        return {"status": "fertig", "ausgabe": r.stdout}
    finally:
        lock.release()
