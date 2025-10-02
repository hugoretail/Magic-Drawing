"""
Color quantization using OpenCV k-means.

quantize_bgr_kmeans(img_bgr, k) -> (quant_bgr, labels, palette_bgr)
"""

from __future__ import annotations

import numpy as np


def quantize_bgr_kmeans(img_bgr: np.ndarray, k: int):
	import cv2

	h, w = img_bgr.shape[:2]
	#prepare samples Nx3 float32
	samples = img_bgr.reshape((-1, 3)).astype(np.float32)
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
	attempts = 1
	flags = cv2.KMEANS_PP_CENTERS
	#provide an initial label array to satisfy type checkers
	best_labels = np.zeros((samples.shape[0], 1), dtype=np.int32)
	compactness, labels, centers = cv2.kmeans(samples, k, best_labels, criteria, attempts, flags)
	centers = np.clip(centers, 0, 255).astype(np.uint8)
	labels = labels.reshape((h, w)).astype(np.int32)
	quant = centers[labels]
	palette = centers  #BGR uint8, shape (k, 3)
	return quant, labels, palette
