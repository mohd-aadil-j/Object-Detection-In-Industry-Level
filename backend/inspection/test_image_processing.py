from pathlib import Path
from tempfile import TemporaryDirectory

import cv2
import numpy as np
from django.test import SimpleTestCase

from .image_processing import process_image


class ImageProcessingTests(SimpleTestCase):
    def test_extracts_wire_sequence_and_rgb_values(self):
        image = np.full((180, 480, 3), 255, dtype=np.uint8)
        colors = [(0, 255, 255), (255, 0, 0), (0, 0, 0), (0, 0, 255)]
        for index, color in enumerate(colors):
            x = 20 + index * 110
            cv2.rectangle(image, (x, 50), (x + 70, 130), color, -1)

        with TemporaryDirectory() as directory:
            image_path = Path(directory) / "wires.png"
            cv2.imwrite(str(image_path), image)
            processed = process_image(image_path)

        self.assertEqual(processed.sequence, ["yellow", "blue", "black", "red"])
        self.assertEqual(len(processed.wires), 4)
        self.assertEqual(processed.wires[0].rgb, (255, 255, 0))

    def test_ignores_white_background(self):
        image = np.full((100, 100, 3), 255, dtype=np.uint8)
        with TemporaryDirectory() as directory:
            image_path = Path(directory) / "empty.png"
            cv2.imwrite(str(image_path), image)
            processed = process_image(image_path)

        self.assertEqual(processed.sequence, [])
