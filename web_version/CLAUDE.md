# Web Version — MNIST Digit Recognition

Browser-based version of the shared MNIST digit recognizer. See the project
root `CLAUDE.md` for the overall architecture and shared commands.

## Project Overview

`server.py` runs a local `ThreadingHTTPServer` that serves the drawing page
and a `/predict` endpoint. The page (`templates/index.html` +
`static/app.js` + `static/style.css`) lets the user draw a digit on an HTML
`<canvas>`, sends it as a PNG data URL to `/predict`, and displays the
predicted digit and confidence returned by the shared model.

## Commands

- Run from the project root: `python web_version/server.py`
- Opens `http://127.0.0.1:8000` automatically; stop with `Ctrl+C`
- Windows: double-click `run_web.bat` (creates `.venv`, installs
  dependencies, then launches the server)

## Tech Stack

- Python standard library `http.server` (`BaseHTTPRequestHandler`,
  `ThreadingHTTPServer`) — no web framework
- Vanilla HTML/CSS/JavaScript on the frontend, no build step or bundler
- Pillow to decode the incoming PNG and run it through `mnist_model.py`

## Architecture

- `ROUTES` maps `GET /`, `GET /app.js`, `GET /style.css` to static files
  under `templates/` and `static/`.
- `DigitHandler.do_GET` serves those static routes; `do_POST` handles
  `POST /predict`.
- `/predict` expects JSON `{"image": "data:image/png;base64,..."}`, decodes
  the base64 PNG with Pillow, calls `predict_digit(model, image)` from
  `mnist_model.py`, and returns `{"digit": ..., "confidence": ...}` as JSON.
  Invalid input returns HTTP 400; unexpected errors return HTTP 500 with a
  generic message (the real error is only printed server-side).
- `static/app.js` tracks pointer events to draw on the canvas, resets the
  canvas to black on load/clear, and posts the canvas contents to
  `/predict` on **Recognize**.
- `main()` loads (or trains) the model once via `load_or_train_model()`
  before starting the server.

## Code Style

- Use browser-native HTML canvas and JavaScript; no frontend framework.
- Use only the Python standard library for the server (no Flask/FastAPI).
- Send the canvas as PNG data URLs to `/predict`.
- Keep the page usable with keyboard focus and clear status text
  (`role="status"` / `aria-live="polite"` on the result element).
- Code, comments, and server-side log messages stay in English.

## Development Notes

- The model loads once when the server starts; each request reuses it.
- Request bodies larger than 2,000,000 bytes are rejected as invalid to
  avoid unbounded memory use from a malformed request.
- Codex originally implemented this application; see the root `CLAUDE.md`
  and `README.md` for the full development history.
