# Desktop Version — MNIST Digit Recognition

Tkinter desktop application for the shared MNIST digit recognizer. See the
project root `CLAUDE.md` for the overall architecture and shared commands.

## Project Overview

`digit_recognition.py` opens a Tkinter window with a black drawing canvas.
The user draws a digit with the mouse, presses **Recognize**, and the app
shows the predicted digit and confidence using the shared model in
`../mnist_model.py`.

## Commands

- Run from the project root: `python desktop_version/digit_recognition.py`
- Windows: double-click `run_desktop.bat` (creates `.venv`, installs
  dependencies, then launches the app)

## Tech Stack

- Tkinter (standard library) for the GUI
- Pillow (`Image`, `ImageDraw`) to mirror the on-screen drawing into an
  in-memory image that is fed to the model

## Architecture

- `DigitRecognitionApp` owns the Tkinter widgets, a `Canvas` for display, and
  a parallel Pillow `Image`/`ImageDraw` pair (`self.image`) that records the
  same strokes for prediction.
- Mouse events: `start_stroke` records the first point, `draw_stroke` draws a
  line segment on both the canvas and the Pillow image, `end_stroke` resets
  the tracked point.
- `clear()` wipes both the canvas and the backing image.
- `recognize()` calls `predict_digit(self.model, self.image)` from
  `mnist_model.py` and shows the result, or an info dialog if the canvas is
  blank (`ValueError` from `preprocess_image`).
- `main()` loads (or trains) the model once via `load_or_train_model()`, then
  starts the Tkinter main loop.

## Code Style

- Use Tkinter for the interface (do not swap in another GUI toolkit).
- Keep the Pillow image synchronized with every stroke drawn on the canvas.
- Reuse the shared model and preprocessing code from the project root instead
  of reimplementing it here.
- Keep the Clear and Recognize actions visible and keyboard accessible.
- Code and comments stay in English.

## Development Notes

- The model loads once at startup (`main()`); avoid reloading it per
  prediction.
- Codex originally implemented this application; see the root `CLAUDE.md`
  and `README.md` for the full development history.
