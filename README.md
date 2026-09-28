# S1 IPTV Channel Directory and Remote Sender

A small Python HTTP application with:
- Channel directory and search/filter interface (`iptv_sender.html`)
- S1 TV playback client (`iptv_client.html`)
- Python HTTP host/API (`iptv_host.py`)
- Optional Windows Tkinter control panel (`S1_Control_Panel.py`)

## Run locally (Windows)

1. Install Python 3.10 or newer.
2. Keep all project files in the same folder.
3. Run `python iptv_host.py` or double-click/run `S1_Control_Panel.py`.
4. Sender/Center: `http://127.0.0.1:8000/`
5. S1 TV client: `http://127.0.0.1:8000/s1`

The Windows control panel is a local desktop tool; it is not run by cloud hosting.

## Deploy the web app

This project requires a Python server because the sender and TV client use `/api/push`, `/api/current`, and `/api/default`. GitHub Pages alone cannot run these API endpoints.

### Render

1. Push this repository to GitHub.
2. In Render, create a new Web Service and connect the repository.
3. Set Build Command to `pip install -r requirements.txt`.
4. Set Start Command to `python iptv_host.py`.
5. Deploy. Render supplies the `PORT` environment variable, which the host reads.
6. Open the deployed service URL for the Center; append `/s1` for the TV client.

The free hosting tier, if available to your account, may sleep or restart. Current channel selection is in memory and resets on restart. The default channel is written to `iptv_default.json`; ephemeral cloud filesystems may not preserve it across redeploys/restarts. Use a persistent disk or database for durable cloud storage.

## GitHub upload

Create a repository, then upload/commit the contents of this folder (not the ZIP file itself, unless you prefer to keep it as an archive).

## Important notes

- The included channel directory contains stream URLs supplied in the original project. Availability, geographic restrictions, provider terms, and rights vary. Only access or redistribute streams you are authorized to use.
- Public repositories expose all committed source and stream URLs. Remove private credentials, tokens, or URLs before publishing.
- Many streams may not play in browser due to provider CORS, HTTPS/mixed-content, codec, geo-restrictions, or stream availability.
- This app does not proxy or rebroadcast video; it sends the selected stream URL to the browser client.
