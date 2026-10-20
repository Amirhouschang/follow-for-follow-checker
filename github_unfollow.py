"""
GitHub: Wer folgt mir nicht zurück? -> entfolgen

Nutzung:
    export GITHUB_TOKEN="dein_token"
    python github_unfollow.py            # nur anzeigen (Probelauf)
    python github_unfollow.py --apply    # wirklich entfolgen

Token:
    GitHub > Settings > Developer settings > Personal access tokens
    - Classic: Scope "user:follow"
    - Fine-grained: Account permission "Followers" = Read and write
"""

import os
import sys
import time
import requests

USERNAME = "Amirhouschang"
API = "https://api.github.com"

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


def main():
    apply = "--apply" in sys.argv

    followers = get_all(f"/users/{USERNAME}/followers")
    following = get_all(f"/users/{USERNAME}/following")
    not_following_back = sorted(following - followers, key=str.lower)

    print(f"Follower:  {len(followers)}")
    print(f"Ich folge: {len(following)}")
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
