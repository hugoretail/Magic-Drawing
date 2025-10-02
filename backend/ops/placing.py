"""
Placement of numbers inside regions.

Given regions (from segments.extract_regions) and outline mask (optional),
return a list of placements: (x, y, label) for drawing text.
"""

from __future__ import annotations

from typing import List, Dict, Tuple

import numpy as np


def _safe_point_in_mask(mask_roi: np.ndarray) -> Tuple[int, int]:
	"""Pick a point inside the ROI mask, preferring the center of largest distance transform.
	mask_roi: uint8 0/1
	returns (px, py) coords within the ROI frame.
	"""
	import cv2

	if mask_roi.dtype != np.uint8:
		mask_roi = mask_roi.astype(np.uint8)
	#distance transform works on binary 0/255
	bin255 = (mask_roi > 0).astype(np.uint8) * 255
	if bin255.max() == 0:
		return 0, 0
	dist = cv2.distanceTransform(bin255, cv2.DIST_L2, 3)
	y, x = np.unravel_index(np.argmax(dist), dist.shape)
	return int(x), int(y)


def place_numbers(regions: List[Dict], outline_mask: np.ndarray | None = None) -> List[Tuple[int, int, int]]:
	placements: List[Tuple[int, int, int]] = []
	for r in regions:
		x, y, w, h = r["bbox"]
		mx, my = _safe_point_in_mask(r["mask"])  #local ROI coords
		px = x + mx
		py = y + my
		placements.append((int(px), int(py), int(r["label"])))
	return placements
