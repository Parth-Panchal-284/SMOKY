# DATA ER

Clinical operations console for an AI-powered data repair system.

RocketRide orchestrates specialist agents in parallel. Hotdata gives each specialist an isolated task-scoped database. The Operating Room screen makes that execution visible.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints (typically http://localhost:8501).

`DEMO_MODE` is on by default. The UI runs with a deterministic mock timeline — no backend required.

## Connect RocketRide events

Replace the stub in [`services/backend_client.py`](services/backend_client.py):

- `poll_events(run_id, cursor, elapsed)` — the function the UI calls every second
- `fetch_live_events(...)` — put the real HTTP / SSE / websocket client here
- Set `DEMO_MODE = False` (or env `DATA_ER_DEMO_MODE=0`) when the live adapter is ready

UI components never import the mock source. After go-live you can delete [`services/mock_events.py`](services/mock_events.py).
