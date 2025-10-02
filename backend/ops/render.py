
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
	#ensure mask shape
	if outline_mask.shape[:2] != (h, w):
		outline_mask = cv2.resize(outline_mask, (w, h), interpolation=cv2.INTER_NEAREST)
	#draw black where mask is 255
	canvas[outline_mask > 0] = (0, 0, 0)
	return canvas


def draw_numbers(img_bgr: np.ndarray, placements: list[tuple[int, int, int]]) -> np.ndarray:
	"""Draw region numbers using OpenCV putText.
	placements: list of (x, y, labelIndex). We draw labelIndex+1 as the human-facing number.
	"""
	import cv2

	out = img_bgr.copy()
	for (x, y, lbl) in placements:
		text = str(int(lbl) + 1)
		cv2.putText(out, text, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness=1, lineType=cv2.LINE_AA)
	return out


def labels_viz(label_map: np.ndarray, palette_bgr: np.ndarray | None = None) -> np.ndarray:
	import cv2
	h, w = label_map.shape[:2]
	if palette_bgr is None:
		#create a simple palette per unique label
		unique = np.unique(label_map)
		k = unique.size
		rng = np.random.default_rng(123)
		pal = (rng.integers(0, 255, size=(k, 3))).astype(np.uint8)
		#map unique labels to 0..k-1
		remap = {int(u): i for i, u in enumerate(unique.tolist())}
		indexed = np.vectorize(lambda v: remap[int(v)])(label_map)
		return pal[indexed]
	else:
		pal = palette_bgr
		pal_len = pal.shape[0]
		indexed = np.clip(label_map, 0, pal_len - 1)
		return pal[indexed]
