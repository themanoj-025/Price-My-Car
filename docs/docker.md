# Price-My-Car (AutoIntel) — Docker Guide

## Quick start

```bash
docker compose up -d
```

One service (`app`) serves the Streamlit dashboard on **http://localhost:8501**.
The dataset (`Cleaned_Car_data.csv`) and ML artifacts in `ml_ready/` ship
inside the image. If models are absent, the app falls back to demo mode.

## Environment

No secrets are required. Auth accounts are created through the UI and
stored in `users_db.json` in the app working directory.

## Persisting the auth database

The app writes `users_db.json` to its working dir (`/app/users_db.json`).
Container filesystems are ephemeral, so to keep accounts across restarts
add a bind mount in `docker-compose.prod.yml`:

```yaml
services:
  app:
    volumes:
      - ./users_db.json:/app/users_db.json
```

## Development

```bash
make up   # dev override: bind mounts + hot reload (polling watcher)
```

Source edits to `streamlit_app.py` / `helpers.py` are picked up live.

## Production

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Restart `always`, memory limit 2G, no dev mounts.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Dashboard says "Demo Mode" | ML artifacts missing — run `docker compose exec app python prepare_ml_data.py` then `train_dashboard_models.py`, or rebuild after adding them |
| Blank page / slow load | Large model files (random_forest.pkl ~40MB); give the healthcheck `start_period` time |
| Port 8501 in use | Change `ports` in `docker-compose.yml` |
| Accounts reset on restart | Add the `users_db.json` bind mount (see above) |
