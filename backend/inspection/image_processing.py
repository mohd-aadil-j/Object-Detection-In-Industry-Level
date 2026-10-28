from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


COLOR_PALETTE = {
    "red": (0, 0, 255),
    "yellow": (0, 255, 255),
    "green": (0, 180, 0),
    "blue": (255, 0, 0),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "orange": (0, 165, 255),
    "purple": (128, 0, 128),
}


@dataclass(frozen=True)
class DetectedWire:
    color: str
    rgb: tuple[int, int, int]
    center: tuple[int, int]
    layer: int


@dataclass(frozen=True)
class ProcessedImage:
    wires: list[DetectedWire]
    mask: np.ndarray

    @property
    def sequence(self):
        return [wire.color for wire in self.wires]


def _wire_mask(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]
    colored_pixels = saturation > 35
    dark_pixels = value < 90
    mask = np.where(colored_pixels | dark_pixels, 255, 0).astype(np.uint8)
    kernel = np.ones((3, 3), dtype=np.uint8)
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)


def _nearest_color(rgb):
    pixel = np.array(rgb, dtype=np.float32)
    name, bgr = min(
        COLOR_PALETTE.items(),
        key=lambda item: np.linalg.norm(pixel - np.array(item[1], dtype=np.float32)),
    )
    return name


def process_image(image_path: str | Path, layer_distance: int = 0):
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Unable to read inspection image: {image_path}")

    mask = _wire_mask(image)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 100:
            continue
        x, y, width, height = cv2.boundingRect(contour)
        region = image[y : y + height, x : x + width]
        region_mask = mask[y : y + height, x : x + width]
        pixels = region[region_mask > 0]
        if pixels.size == 0:
            continue
        bgr = tuple(np.median(pixels, axis=0).astype(int).tolist())
        center = (x + width // 2, y + height // 2)
        candidates.append((center, bgr))

    candidates.sort(key=lambda item: (item[0][1], item[0][0]))
    wires = []
    layer_centers = []
    for center, bgr in candidates:
        if layer_distance > 0:
            matching_layer = next(
                (
                    index
                    for index, layer_y in enumerate(layer_centers)
                    if abs(center[1] - layer_y) <= layer_distance
                ),
                None,
            )
            if matching_layer is None:
                layer_centers.append(center[1])
                matching_layer = len(layer_centers) - 1
        else:
            matching_layer = 0
        wires.append(
            DetectedWire(
                color=_nearest_color(bgr),
                rgb=(bgr[2], bgr[1], bgr[0]),
                center=center,
                layer=matching_layer,
            )
        )

    wires.sort(key=lambda wire: (wire.layer, wire.center[0], wire.center[1]))
    return ProcessedImage(wires=wires, mask=mask)
