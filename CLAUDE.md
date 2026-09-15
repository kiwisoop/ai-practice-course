# MNIST Handwritten Digit Recognition

A desktop and web application that recognizes a mouse-drawn digit (0-9) using a
convolutional neural network trained on the MNIST dataset. The base
implementation was generated with Codex; this file and the per-folder
`CLAUDE.md` files were added with Claude Code to match the class submission
format.

## Project Overview

The user draws a single digit on a black canvas. The drawing is cropped,
resized, and centered into a 28x28 tensor, then classified by a small CNN.
The desktop app (Tkinter) and the web app (HTML Canvas + Python HTTP server)
both call the same model and preprocessing code in `mnist_model.py`.

## Commands

- Install dependencies: `python -m pip install -r requirements.txt`
- Run desktop app: `python desktop_version/digit_recognition.py`
- Run web app: `python web_version/server.py` (opens `http://127.0.0.1:8000`)
- Run tests: `python -m unittest discover -s tests`
- Windows shortcuts: `desktop_version/run_desktop.bat`, `web_version/run_web.bat`
  (each creates a `.venv`, installs dependencies, then launches the app)

## Tech Stack

- Python 3.11 recommended (Python 3.9+ is also supported)
- TensorFlow/Keras for the CNN model
- Pillow and NumPy for image preprocessing
- Tkinter for the desktop GUI
- Python standard-library `http.server` for the web backend
- Vanilla HTML/CSS/JavaScript for the web frontend (no build step)

## Architecture

```
Study-01/
├── CLAUDE.md                 # this file (root rules for Claude Code)
├── README.md / SUBMISSION.md # course submission docs
├── mnist_model.py            # shared model: train/load, preprocess, predict
├── mnist_model.keras         # trained model, reused by both apps
├── requirements.txt
├── desktop_version/
│   ├── CLAUDE.md             # desktop-specific rules
│   ├── digit_recognition.py  # Tkinter app
│   └── run_desktop.bat
├── web_version/
│   ├── CLAUDE.md             # web-specific rules
│   ├── server.py             # ThreadingHTTPServer + /predict endpoint
│   ├── run_web.bat
│   ├── templates/index.html
│   └── static/{app.js,style.css}
└── tests/test_preprocessing.py
```

Key functions in `mnist_model.py`:

- `preprocess_image(image)` — crops the drawn digit's bounding box, scales the
  longer side to 20px, centers it in a 28x28 black canvas, and normalizes
  pixel values to `[0, 1]`. Raises `ValueError` on a blank drawing.
- `load_or_train_model()` — loads `mnist_model.keras` if present; otherwise
  downloads MNIST, trains a 3-epoch CNN, and saves the model.
- `predict_digit(model, image)` — returns `(digit, confidence)`.

Both `desktop_version/digit_recognition.py` and `web_version/server.py` add
the project root to `sys.path` and import these three functions directly
instead of duplicating model or preprocessing logic.

## Code Style

- All Python code and comments are in English.
- Keep the shared model/preprocessing logic only in `mnist_model.py`; do not
  duplicate it in the desktop or web version.
- Validate user input (e.g. a blank canvas) and surface understandable error
  messages instead of raw stack traces.
- Keep each app small and readable; avoid adding frameworks or abstractions
  the assignment does not need.

## Development Notes

- `mnist_model.keras` is already trained and committed; do not retrain it
  unless the model file is missing or intentionally being replaced.
- `.gitignore` excludes `.venv/`, `__pycache__/`, `.pytest_cache/`,
  `.DS_Store`, and `memo.txt` (the instructor-facing task notes used to
  drive Claude Code, not part of the submitted program). Never commit
  virtual environments, credentials, or API keys.
- Codex originally implemented the desktop and web applications; Claude Code
  added this `CLAUDE.md` hierarchy and cleaned up the documentation to match
  the class submission format. See `README.md` for the full history.
