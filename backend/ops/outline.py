"""
Outline extraction using Canny + dilation.

Given a BGR uint8 image and desired thickness, returns a binary outline mask
as uint8 (0 background, 255 edges).
"""

from __future__ import annotations

import numpy as np


def outline_edges(img_bgr: np.ndarray, thickness: int = 2) -> np.ndarray:
	import cv2

	gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
	m = np.median(gray)
	lower = int(max(0, 0.66 * m))
	upper = int(min(255, 1.33 * m))
	edges = cv2.Canny(gray, lower, upper)
	if thickness > 1:
		k = max(1, thickness)
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
		edges = cv2.dilate(edges, kernel)
	return edges
