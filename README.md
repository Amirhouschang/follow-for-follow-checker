# GitHub Traffic und Follow-back Check

**Deutsch** | [English](README.en.md)

Zwei kleine Python-Skripte für zwei Fragen:

1. Schaut sich überhaupt jemand meine Projekte an?
2. Wer folgt mir, und wem folge ich nur einseitig?

## Warum dieses Projekt

Ich habe vor ein paar Tagen darüber nachgedacht, warum mir auf GitHub Leute folgen, die ich gar nicht kenne. Oder warum sich Leute auf LinkedIn mit mir vernetzen, obwohl ich sie weder kenne noch je Kontakt mit ihnen hatte. Deswegen dachte ich: Okay, ich checke mal, ob diese Menschen sich überhaupt jemals meine Repos angeschaut haben.

Außerdem habe ich mich an einigen Stellen beworben und bei jeder Bewerbung ein paar Projekte im Lebenslauf verlinkt. Ich wollte wissen, ob überhaupt jemand reinschaut. Ich war erstaunt, es wurde nicht wirklich geschaut. Die Zahlen waren deutlich, deutlich niedriger als diese kleine Gruppe, die mir folgt.

Für mich war das alles sehr neu. GitHub kannte ich vorher nur von Dokumentationen, die ich ab und zu für meine eigenen privaten Sachen nutze. Seit ich ein paar Repos gepostet habe, kommen diese Follower. Ich selbst habe fast niemandem von mir aus gefolgt. Die Leute sind mir zuerst gefolgt, und danach bin ich ihnen zurückgefolgt. Wie ein naiver Mensch habe ich mir ihre Profile angeschaut und dazu ihre Repos, vielleicht nicht alle, aber einige schon. Mein LinkedIn ist auch super neu, denn soziale Netzwerke hatte ich als Autist nicht. Darin bin ich auch nicht besonders begabt, und lustig war das Ganze nicht wirklich.

Danach habe ich ein bisschen recherchiert und Follow for Follow entdeckt. Ich dachte nur: Wow, wie blöd ist diese Aktion, und was für ein Unsinn ist das Ganze. Dann dachte ich: Okay, wenn das so ist, lasse ich das bleiben, auch wenn ich gar nicht verstehe, worum es dabei geht und warum. Ob man gesehen wird oder nicht, ist für mich total uninteressant. Trotzdem dachte ich: Wenn es schon Follow for Follow gibt, will ich wenigstens wissen, wer mir folgt und wer mich danach wieder entfolgt. Wenn du das liest, gehörst du bestimmt nicht zu dieser Gruppe, also nimm es nicht persönlich! Aber ich liebe sie trotzdem, auch wenn ich sie nicht verstehe. Hahaha

Aber dafür habe ich keine Zeit. Ich bin kein Mensch, der tausende andere Menschen sucht, ihnen folgt und sie wieder entfolgt. Deswegen dieses Python-Skript. Ich automatisiere zurzeit mein gesamtes Leben, das gehört dazu und macht mir mehr Spaß.

## Was die Skripte machen

### `github_traffic.py`

- holt für alle eigenen Repos Aufrufe, Besucher, Clones, Herkunftsseiten und die meistbesuchten Dateien
- speichert den Verlauf von Aufrufen, Clones, Herkunftsseiten und Dateien als CSV, weil GitHub selbst nur die letzten 14 Tage speichert
- erstellt einen Excel-Bericht mit vier Blättern: Übersicht, Verlauf (Aufrufe und Clones pro Tag), Herkunft, Dateien

### `github_unfollow.py`

- vergleicht, wer mir folgt und wem ich folge
- zeigt, wer nicht zurückfolgt
- speichert bei jedem Lauf den Follower-Stand und zeigt, wer seit dem letzten Lauf neu dazugekommen ist oder dich entfolgt hat
- hält diese Änderungen mit Datum in `follower_aenderungen.csv` fest
- startet standardmäßig als Probelauf, entfolgt wird nur mit `--apply`

**Wichtig:** „Folgt nicht zurück“ heißt nicht „hat mich entfolgt“. Entfolger erkennt das Skript erst ab dem zweiten Lauf, weil es dafür einen gespeicherten Stand zum Vergleich braucht.

**Hinweis:** Organisationen (zum Beispiel `jupyter` oder `docker`) können niemandem folgen. Sie stehen deshalb immer in der Liste. Die Liste also vor `--apply` prüfen.

## Was die Daten nicht verraten

- GitHub zeigt nie, **wer** ein Repo angeschaut hat, nur **wie viele**.
- Eigene Besuche werden mitgezählt. Ein Repo mit genau einem Besucher war also oft man selbst.

## Installation

```bash
pip install requests pandas openpyxl
```

Einen Personal Access Token (classic) erstellen unter
GitHub > Settings > Developer settings > Personal access tokens.

Benötigte Berechtigungen:

- `repo` für die Traffic-Daten
- `user:follow` zum Entfolgen

Den Token als Umgebungsvariable setzen, **nie direkt ins Skript schreiben**:

```bash
export GITHUB_TOKEN="dein_token"
```

In `github_unfollow.py` den eigenen Benutzernamen bei `USERNAME` eintragen.

## Nutzung

```bash
# Traffic-Bericht
python github_traffic.py

# Follow-back-Check (nur anzeigen)
python github_unfollow.py

# wirklich entfolgen
python github_unfollow.py --apply
```

## Automatisierung mit n8n

Der Traffic-Bericht läuft bei mir automatisch einmal pro Tag, sobald der Laptop an ist. n8n läuft in Docker und kann Python auf dem Laptop nicht direkt starten. Deshalb ruft n8n einen kleinen lokalen Dienst auf, der das Skript startet.

```
n8n (Docker, jede Stunde)  >  POST http://172.17.0.1:8766/run  >  github_service.py  >  github_traffic.py
```

- **n8n** fragt jede Stunde beim lokalen Dienst nach
- **`github_service.py`** (FastAPI) startet `github_traffic.py` nur, wenn es heute noch nicht gelaufen ist. Das Datum steht in `last_run.txt`
- **systemd** startet den Dienst automatisch beim Login

### Dateien

| Datei | Zweck |
|---|---|
| `github_service.py` | lokaler Dienst für n8n (Port 8766) |
| `github_traffic_workflow.json` | n8n-Workflow zum Importieren |
| `.env` | `GITHUB_TOKEN` und `SERVICE_API_KEY` (gehört nicht ins Repo) |

### Einrichten

1. Zusätzliche Pakete installieren:

```bash
pip install fastapi uvicorn python-dotenv
```

2. Im Projektordner eine `.env` anlegen:

```
GITHUB_TOKEN=dein_token
SERVICE_API_KEY=ein_eigener_geheimer_schluessel
```

3. Dienst für systemd anlegen unter `~/.config/systemd/user/github-traffic.service` (Pfade anpassen):

```ini
[Unit]
Description=GitHub Traffic Dienst fuer n8n (Port 8766)
After=network-online.target

[Service]
WorkingDirectory=/home/<user>/Dokumente/Github_projects/github_traffic
ExecStart=/home/<user>/miniconda3/envs/jupyter-env/bin/uvicorn github_service:app --host 172.17.0.1 --port 8766
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

4. Dienst einschalten:

```bash
systemctl --user daemon-reload
systemctl --user enable --now github-traffic.service
systemctl --user status github-traffic.service
```

5. In n8n `github_traffic_workflow.json` importieren, im HTTP-Node eine Header-Auth-Credential mit Name `X-API-Key` und dem Wert von `SERVICE_API_KEY` auswählen und den Workflow aktivieren.

**Wichtig:** `.env` und `last_run.txt` in die `.gitignore` eintragen, damit der Token nie auf GitHub landet.

## Gut zu wissen

- Das Traffic-Skript mindestens alle 14 Tage starten, sonst gehen Daten verloren.
- Mit der n8n-Automatisierung (siehe oben) müsst ihr das Traffic-Skript nicht mehr selbst starten. `github_unfollow.py` läuft weiterhin von Hand.
- Massenhaftes automatisches Entfolgen sieht GitHub nicht gern. Das Skript wartet deshalb eine Sekunde zwischen jeder Aktion.
