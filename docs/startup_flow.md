# Startup Flow — Price-My-Car

## 1. Local Development

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Boot sequence inside `app/streamlit_app.py`:
1. **Path bootstrap** — repo root inserted into `sys.path` (enables `from app.helpers import ...` regardless of CWD).
2. **Page config** — `st.set_page_config` (title/icon/layout).
3. **CSS injection** — dark theme styles, glass cards, animations.
4. **Session state init** — auth + UI defaults (`init_session_state()`).
5. **Artifact loading (cached)** — `data/Cleaned_Car_data.csv`, `ml_ready/preprocessor.pkl`, `ml_ready/models/*`, `ml_ready/*.npy`; if any load fails or no models exist → **demo mode** with synthetic data + info banner.
6. **Render** — sidebar (nav, quick stats, filters, expert mode) → 9 pages. Server ready on `:8501`.

## 2. Docker (prod)

```
docker build -t autointel .
docker compose up -d
```

1. `deps` stage: `pip install -r requirements.txt`.
2. `prod` stage: `COPY app/`, `COPY scripts/backfills/prepare_ml_data.py`, `COPY data/`, `COPY ml_ready/`, `COPY .streamlit/`.
3. `RUN python scripts/backfills/prepare_ml_data.py` — regenerates gitignored `.npy` files at build time (build fails loudly if the CSV is missing/unreadable, never ships a silent demo-mode image).
4. `CMD ["streamlit", "run", "app/streamlit_app.py", ...]` as `appuser`.
5. Healthcheck: `curl /_stcore/health` (30s interval, 60s start period).

## 3. Docker (dev — hot reload)

`docker compose -f docker-compose.yml -f docker-compose.dev.yml up`:
- Bind mounts: `./app`, `./tests`, `./scripts`, `./data`, `./ml_ready`, `./users_db.json`.
- `--server.fileWatcherType=polling --server.runOnSave=true` for live reload.
- Makefile `up` touches `users_db.json` first so the bind mount is a file, not a directory.

## 4. Streamlit Cloud

`setup.sh` runs before the app starts:
1. Creates `ml_ready/models/` if missing.
2. If `ml_ready/X_train.npy` or `preprocessor.pkl` missing → `python scripts/backfills/prepare_ml_data.py`.
3. If `ml_ready/models/linear_regression.pkl` missing → `python scripts/seed/train_dashboard_models.py`.
4. App starts via `streamlit run app/streamlit_app.py` (declared app entry in the Cloud console).

## 5. CI (push/PR)

`ci.yml` `test` job: install deps → `py_compile` `app/helpers.py`, `app/streamlit_app.py`, `tests/test_helpers.py` → `pytest tests/test_helpers.py`. `docker` job: compose validation → `docker build` → trivy scan. Link-check job scans docs.

## 6. Failure Modes & Behavior

| Failure | Behavior |
| --- | --- |
| Missing CSV / artifacts | Demo mode with `st.info` banner; app still serves (by design). |
| Broken prep at Docker build | Build fails loudly — no silent demo image. |
| `users_db.json` absent | Created empty at first write; Makefile pre-touches for bind-mount safety. |
| Tests fail | CI red — 65 tests must pass. |
