
from __future__ import annotations

import numpy as np


def compose_worksheet(outline_mask: np.ndarray, shape_hw3: tuple[int, int, int]) -> np.ndarray:
	"""Return a BGR worksheet image (white background, black outline).

	outline_mask: uint8 0/255 edges
	shape_hw3: target (H, W, 3)
	"""
	import cv2

	h, w, c = shape_hw3
	assert c == 3
	canvas = np.full((h, w, 3), 255, dtype=np.uint8)
	# ensure mask shape
	if outline_mask.shape[:2] != (h, w):
		outline_mask = cv2.resize(outline_mask, (w, h), interpolation=cv2.INTER_NEAREST)
	# draw black where mask is 255
	canvas[outline_mask > 0] = (0, 0, 0)
	return canvas
