
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


def legend_viz(palette_bgr: np.ndarray, box_size: int = 40, font_scale: float = 0.7, thickness: int = 2) -> np.ndarray:
	import cv2
	K = palette_bgr.shape[0]
	margin = 16
	width = box_size * K + margin * 2
	height = box_size + 40
	canvas = np.full((height, width, 3), 255, dtype=np.uint8)
	for i in range(K):
		color = tuple(int(x) for x in palette_bgr[i])
		x = margin + i * box_size
		y = margin
		cv2.rectangle(canvas, (x, y), (x + box_size - 1, y + box_size - 1), color, -1)
		cv2.rectangle(canvas, (x, y), (x + box_size - 1, y + box_size - 1), (0, 0, 0), 1)
		text = str(i + 1)
		(text_w, text_h), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
		text_x = x + (box_size - text_w) // 2
		text_y = y + box_size + text_h + 2
		cv2.putText(canvas, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)
	title = ""
	(text_w, text_h), baseline = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
	title_x = (width - text_w) // 2
	title_y = margin - 4 + text_h
	cv2.putText(canvas, title, (title_x, title_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, cv2.LINE_AA)
	return canvas


def overlay_legend_on_worksheet(worksheet: np.ndarray, legend: np.ndarray, margin: int = 12, alpha: float = 0.95) -> np.ndarray:
	h, w = worksheet.shape[:2]
	lh, lw = legend.shape[:2]
	max_lw = min(w // 2, lw)
	max_lh = min(h // 4, lh)
	if lw > max_lw or lh > max_lh:
		import cv2
		legend = cv2.resize(legend, (max_lw, max_lh), interpolation=cv2.INTER_AREA)
		lh, lw = legend.shape[:2]
	x0 = w - lw - margin
	y0 = margin
	roi = worksheet[y0:y0+lh, x0:x0+lw]
	blended = (roi * (1 - alpha) + legend * alpha).astype(np.uint8)
	worksheet_out = worksheet.copy()
	worksheet_out[y0:y0+lh, x0:x0+lw] = blended
	return worksheet_out
