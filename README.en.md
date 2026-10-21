# GitHub Traffic and Follow-back Check

[Deutsch](README.md) | **English**

Two small Python scripts for two questions, plus a small service for automation with n8n:

1. Is anyone actually looking at my projects?
2. Who follows me, and who do I follow one-sidedly?

> **Note:** The code comments, terminal output and Excel sheets are in German. Sorry, people!

## Why this project

A few days ago I was wondering why people I don't even know follow me on GitHub. Or why people connect with me on LinkedIn, even though I neither know them nor have ever been in contact with them. So I thought: Okay, let me check whether these people have ever even looked at my repos.

I have also applied to a few places and linked some projects in my CV for every application. I wanted to know if anyone looks at them at all. I was surprised, nobody really did. The numbers were much, much lower than this small group that follows me.

All of this was very new to me. Before, I only knew GitHub from documentation that I use now and then for my own private stuff. Since I posted a few repos, these followers keep coming. I myself have hardly followed anyone on my own. People followed me first, and then I followed them back. Like a naive person, I looked at their profiles and their repos too, maybe not all of them, but quite a few. My LinkedIn is also super new, because as an autistic person I didn't have social networks. I'm not particularly good at it either, and the whole thing wasn't really funny.

Then I did a bit of research and discovered Follow for Follow. I just thought: Wow, how stupid is this whole thing, and what nonsense is all of it. Then I thought: Okay, if that's how it is, I'll leave it be, even though I don't understand at all what it's about and why. Whether you get seen or not is totally uninteresting to me. Still, I thought: If Follow for Follow exists anyway, I at least want to know who follows me and who unfollows me afterwards. If you're reading this, you're definitely not part of that group, so don't take it personally! But I still love them, even though I don't understand them. 😅

But I don't have time for that. I'm not a person who searches for thousands of other people, follows them and unfollows them again. That's why this Python script. I'm currently automating my whole life, this is part of it and it's more fun for me.

## What the scripts do

### `github_traffic.py`

- fetches views, visitors, clones, referrers and the most visited files for all your own repos
- saves the history of views, clones, referrers and files as CSV, because GitHub itself only keeps the last 14 days
- creates an Excel report with four sheets: Übersicht (overview), Verlauf (daily views and clones), Herkunft (referrers), Dateien (files)

### `github_unfollow.py`

- compares who follows you and who you follow
- shows who doesn't follow back
- saves your follower list on every run and shows who has newly followed or unfollowed you since the last run
- records these changes with the date in `follower_aenderungen.csv`
- runs as a dry run by default, it only unfollows with `--apply`

**Important:** "Doesn't follow back" does not mean "unfollowed me". The script can only detect unfollowers from the second run on, because it needs a saved list to compare with.

**Note:** Organizations (for example `jupyter` or `docker`) can't follow anyone. That's why they always show up in the list. So check the list before using `--apply`.

## What the data doesn't tell you

- GitHub never shows **who** looked at a repo, only **how many**.
- Your own visits are counted too. A repo with exactly one visitor was often just you.

## Installation

```bash
pip install -r requirements.txt
```

Create a personal access token (classic) under
GitHub > Settings > Developer settings > Personal access tokens.

Required permissions:

- `repo` for the traffic data
- `user:follow` for unfollowing

Set the token as an environment variable, **never write it directly into the script**:

```bash
export GITHUB_TOKEN="your_token"
```

In `github_unfollow.py`, enter your own username at `USERNAME`.

## Usage

```bash
# traffic report
python github_traffic.py

# follow-back check (display only)
python github_unfollow.py

# actually unfollow
python github_unfollow.py --apply
```

## Automation with n8n

I run the traffic report automatically once a day, as soon as my laptop is on. n8n runs in Docker and can't start Python on the laptop directly. So n8n calls a small local service that starts the script.

```
n8n (Docker, every hour)  >  POST http://172.17.0.1:8766/run  >  github_service.py  >  github_traffic.py
```

- **n8n** asks the local service every hour
- **`github_service.py`** (FastAPI) only starts `github_traffic.py` if it hasn't run today yet. The date is stored in `last_run.txt`
- **systemd** starts the service automatically at login

### Files

| File | Purpose |
|---|---|
| `github_service.py` | local service for n8n (port 8766) |
| `github_traffic_workflow.json` | n8n workflow to import |
| `.env` | `GITHUB_TOKEN` and `SERVICE_API_KEY` (does not belong in the repo) |

### Setup

1. Install the packages (if you haven't already):

```bash
pip install -r requirements.txt
```

2. Create a `.env` in the project folder:

```
GITHUB_TOKEN=your_token
SERVICE_API_KEY=your_own_secret_key
```

3. Create the systemd service at `~/.config/systemd/user/github-traffic.service` (adjust the paths):

```ini
[Unit]
Description=GitHub Traffic service for n8n (port 8766)
After=network-online.target

[Service]
WorkingDirectory=/home/<user>/Documents/github_traffic
ExecStart=/home/<user>/miniconda3/envs/<env>/bin/uvicorn github_service:app --host 172.17.0.1 --port 8766
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

4. Enable the service:

```bash
systemctl --user daemon-reload
systemctl --user enable --now github-traffic.service
systemctl --user status github-traffic.service
```

5. In n8n, import `github_traffic_workflow.json`, select a Header Auth credential with name `X-API-Key` and the value of `SERVICE_API_KEY` in the HTTP node, and activate the workflow.

**Important:** Add `.env` and `last_run.txt` to your `.gitignore` so your token never ends up on GitHub.

## Good to know

- Run the traffic script at least every 14 days, otherwise data gets lost.
- With the n8n automation (see above) you no longer have to start the traffic script yourself. `github_unfollow.py` is still run by hand.
- GitHub doesn't like mass automated unfollowing. That's why the script waits one second between each action.
