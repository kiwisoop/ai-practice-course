# Handwritten Digit Recognition

## Project Overview

Build desktop and web applications that recognize mouse-drawn digits from 0 to 9 with a model trained on MNIST.

## Commands

- Install dependencies: `python -m pip install -r requirements.txt`
- Run desktop app: `python desktop_version/digit_recognition.py`
- Run web app: `python web_version/server.py`
- Run tests: `python -m unittest discover -s tests`

## Tech Stack

- Python 3.11 recommended
- TensorFlow/Keras for the MNIST model
- Pillow and NumPy for image preprocessing
- Tkinter for the desktop interface
- Python standard-library HTTP server for the web interface

## Code Style

- Write code and comments in English.
- Keep the implementation small and readable.
- Reuse the shared `mnist_model.py` module in both applications.
- Validate user input and return understandable errors.

## Development Notes

- The first run downloads MNIST, trains the model, and saves `mnist_model.keras`.
- Later runs reuse the saved model.
- Created with Codex on 2026-09-10.
