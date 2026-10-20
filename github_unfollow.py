"""
GitHub: Wer folgt mir nicht zurück? -> entfolgen
Speichert außerdem bei jedem Lauf den Follower-Stand und zeigt,
wer seit dem letzten Lauf neu dazugekommen ist oder mich entfolgt hat.

Nutzung:
    export GITHUB_TOKEN="dein_token"
    python github_unfollow.py            # nur anzeigen (Probelauf)
    python github_unfollow.py --apply    # wirklich entfolgen

Token:
    GitHub > Settings > Developer settings > Personal access tokens
    - Classic: Scope "user:follow"
    - Fine-grained: Account permission "Followers" = Read and write
"""

import csv
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

import requests

USERNAME = "Amirhouschang"
API = "https://api.github.com"
OUT_DIR = Path(__file__).parent
STAND_DATEI = OUT_DIR / "follower_stand.json"
AENDERUNGEN_DATEI = OUT_DIR / "follower_aenderungen.csv"

token = os.environ.get("GITHUB_TOKEN")
if not token:
    sys.exit("Fehler: GITHUB_TOKEN ist nicht gesetzt.")

HEADERS = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get_all(endpoint):
    """Holt alle Seiten einer Liste (100 Einträge pro Seite)."""
    users, page = [], 1
    while True:
        r = requests.get(
            f"{API}{endpoint}",
            headers=HEADERS,
            params={"per_page": 100, "page": page},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        users.extend(u["login"] for u in data)
        page += 1
    return set(users)


def vergleiche_mit_letztem_stand(followers):
    """Follower mit dem letzten gespeicherten Stand vergleichen und neuen Stand speichern."""
    if not STAND_DATEI.exists():
        print("Erster Lauf: Follower-Stand gespeichert. "
              "Ab dem nächsten Lauf werden Änderungen angezeigt.\n")
    else:
        alt = set(json.loads(STAND_DATEI.read_text(encoding="utf-8")))
        neu = sorted(followers - alt, key=str.lower)
        weg = sorted(alt - followers, key=str.lower)

        print(f"Neue Follower seit letztem Lauf: {len(neu)}")
        for user in neu:
            print(f"  + {user}")
        print(f"Entfolgt seit letztem Lauf: {len(weg)}")
        for user in weg:
            print(f"  - {user}")
        print()

        # Änderungen dauerhaft in CSV festhalten
        if neu or weg:
            datei_neu = not AENDERUNGEN_DATEI.exists()
            heute = date.today().isoformat()
            with AENDERUNGEN_DATEI.open("a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if datei_neu:
                    writer.writerow(["datum", "user", "aenderung"])
                writer.writerows([heute, user, "neu"] for user in neu)
                writer.writerows([heute, user, "entfolgt"] for user in weg)

    STAND_DATEI.write_text(json.dumps(sorted(followers, key=str.lower), indent=2),
                           encoding="utf-8")


def main():
    apply = "--apply" in sys.argv

    followers = get_all(f"/users/{USERNAME}/followers")
    following = get_all(f"/users/{USERNAME}/following")
    not_following_back = sorted(following - followers, key=str.lower)

    print(f"Follower:  {len(followers)}")
    print(f"Ich folge: {len(following)}\n")

    vergleiche_mit_letztem_stand(followers)

    print(f"Folgen nicht zurück: {len(not_following_back)}\n")

    for user in not_following_back:
        if apply:
            r = requests.delete(f"{API}/user/following/{user}", headers=HEADERS, timeout=30)
            status = "entfolgt" if r.status_code == 204 else f"Fehler {r.status_code}"
            print(f"{user}: {status}")
            time.sleep(1)  # API schonen
        else:
            print(f"{user}")

    if not apply and not_following_back:
        print("\nProbelauf. Zum Entfolgen: python github_unfollow.py --apply")


if __name__ == "__main__":
    main()
