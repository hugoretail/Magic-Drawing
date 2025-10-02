"""
Connected components on the label map with min-area filtering.

extract_regions(label_map, min_area) -> list of regions, each region dict contains:

"""

from __future__ import annotations

from typing import List, Dict, Tuple

import numpy as np

"""
  - label: color index (0..K-1)
  - area: pixel area
  - bbox: (x, y, w, h)
  - centroid: (cx, c  y) in image coords (float)
  - mask: ROI boolean mask of shape (h, w) for this component only
"""
def extract_regions(label_map: np.ndarray, min_area: int) -> List[Dict]:

	import cv2

	h, w = label_map.shape[:2]
	regions: List[Dict] = []

	unique_labels = np.unique(label_map)
	for lbl in unique_labels.tolist():
		#build binary mask for this label id
		mask = (label_map == int(lbl)).astype(np.uint8)
		if mask.sum() < min_area:
			#quick skip if total label pixels are small
			continue
		#connected components on this label's mask
		num, comp, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
		#comp is HxW with values in [0..num-1], where 0 is background
		for i in range(1, num):
			area = int(stats[i, cv2.CC_STAT_AREA])
			if area < min_area:
				continue
			x = int(stats[i, cv2.CC_STAT_LEFT])
			y = int(stats[i, cv2.CC_STAT_TOP])
			ww = int(stats[i, cv2.CC_STAT_WIDTH])
			hh = int(stats[i, cv2.CC_STAT_HEIGHT])
			cx, cy = centroids[i]
			#ROI mask for this component only
			comp_mask = (comp == i)
			mask_roi = comp_mask[y:y+hh, x:x+ww]
			regions.append({
				"label": int(lbl),
				"area": area,
				"bbox": (x, y, ww, hh),
				"centroid": (float(cx), float(cy)),
				"mask": mask_roi.astype(np.uint8),
			})

	return regions
