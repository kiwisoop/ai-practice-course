"""Small checks for image preprocessing.

Created with Codex on 2026-09-10.
"""

import unittest

import numpy as np
from PIL import Image, ImageDraw

from mnist_model import preprocess_image


class PreprocessImageTests(unittest.TestCase):
    def test_drawn_digit_is_scaled_and_centered(self) -> None:
        image = Image.new("L", (280, 280), 0)
        ImageDraw.Draw(image).line((130, 30, 130, 250), fill=255, width=18)

        result = preprocess_image(image)

        self.assertEqual(result.shape, (1, 28, 28, 1))
        self.assertEqual(result.dtype, np.float32)
        self.assertGreater(float(result.max()), 0.9)
        self.assertGreater(float(result[0, :, 10:18, 0].sum()), 1.0)

    def test_blank_image_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Draw a digit"):
            preprocess_image(Image.new("L", (280, 280), 0))


if __name__ == "__main__":
    unittest.main()
