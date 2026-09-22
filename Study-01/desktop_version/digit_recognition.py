"""Tkinter desktop application for recognizing handwritten digits.

Created with Codex on 2026-09-10.
"""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from mnist_model import load_or_train_model, predict_digit  # noqa: E402


CANVAS_SIZE = 280
BRUSH_WIDTH = 18


class DigitRecognitionApp:
    """Collect a mouse drawing and display the model prediction."""

    def __init__(self, root: tk.Tk, model) -> None:
        self.root = root
        self.model = model
        self.last_point: tuple[int, int] | None = None
        self.image = Image.new("L", (CANVAS_SIZE, CANVAS_SIZE), 0)
        self.image_draw = ImageDraw.Draw(self.image)

        root.title("MNIST Digit Recognition")
        root.resizable(False, False)

        tk.Label(root, text="Draw one digit from 0 to 9", font=("Arial", 16)).pack(pady=(16, 8))
        self.canvas = tk.Canvas(
            root,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg="black",
            cursor="crosshair",
            highlightthickness=2,
            highlightbackground="#555555",
        )
        self.canvas.pack(padx=20)
        self.canvas.bind("<Button-1>", self.start_stroke)
        self.canvas.bind("<B1-Motion>", self.draw_stroke)
        self.canvas.bind("<ButtonRelease-1>", self.end_stroke)

        controls = tk.Frame(root)
        controls.pack(pady=12)
        tk.Button(controls, text="Clear", width=12, command=self.clear).pack(side=tk.LEFT, padx=6)
        tk.Button(controls, text="Recognize", width=12, command=self.recognize).pack(side=tk.LEFT, padx=6)

        self.result = tk.StringVar(value="Result: -")
        tk.Label(root, textvariable=self.result, font=("Arial", 18, "bold")).pack(pady=(0, 16))

    def start_stroke(self, event: tk.Event) -> None:
        self.last_point = (event.x, event.y)

    def draw_stroke(self, event: tk.Event) -> None:
        if self.last_point is None:
            self.last_point = (event.x, event.y)
            return
        current = (event.x, event.y)
        self.canvas.create_line(
            *self.last_point,
            *current,
            fill="white",
            width=BRUSH_WIDTH,
            capstyle=tk.ROUND,
            smooth=True,
        )
        self.image_draw.line((*self.last_point, *current), fill=255, width=BRUSH_WIDTH)
        self.last_point = current

    def end_stroke(self, _event: tk.Event) -> None:
        self.last_point = None

    def clear(self) -> None:
        self.canvas.delete("all")
        self.image.paste(0, (0, 0, CANVAS_SIZE, CANVAS_SIZE))
        self.result.set("Result: -")

    def recognize(self) -> None:
        try:
            digit, confidence = predict_digit(self.model, self.image)
        except ValueError as error:
            messagebox.showinfo("Nothing to recognize", str(error))
            return
        self.result.set(f"Result: {digit}   Confidence: {confidence:.1%}")


def main() -> None:
    model = load_or_train_model()
    root = tk.Tk()
    DigitRecognitionApp(root, model)
    root.mainloop()


if __name__ == "__main__":
    main()
