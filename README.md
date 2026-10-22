# EcoTrack mobile website

A mobile-friendly Streamlit version of the original command-line EcoTrack project.

## Run locally on Linux Mint

```bash
cd /path/to/the/project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a local URL. Open it on the laptop to test. For phone testing on the same Wi-Fi, use the laptop's local IP and port `8501`, or deploy the project to Streamlit Community Cloud.

## Deploy online

1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and this README.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Create an app, select the repository, branch, and `app.py` as the main file.
4. Deploy. Send the resulting website URL to your sister; she can open it in her phone browser.

## Data persistence warning

This starter version writes records to `ecotrack_data.json` beside the app. On cloud hosting, local files may not survive restarts or redeployments. Before using this for important records, connect a persistent database such as Supabase or another managed database. CSV downloads provide a manual backup.
