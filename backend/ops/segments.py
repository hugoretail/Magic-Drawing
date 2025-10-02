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


def median_smooth_labels(label_map: np.ndarray, ksize: int = 3) -> np.ndarray:
	"""Apply median filtering on label map to remove salt-and-pepper noise.
	Operates per-channel via trick of expanding to 3 channels of same map and collapsing back.
	"""
	import cv2

	# Ensure odd kernel size >= 3
	k = max(3, ksize | 1)
	l = label_map.astype(np.int32)
	# Expand to 3 channels for medianBlur
	l3 = np.repeat(l[..., None], 3, axis=2).astype(np.uint8)
	m3 = cv2.medianBlur(l3, k)
	return m3[..., 0].astype(label_map.dtype)


def merge_micro_regions(label_map: np.ndarray, min_area: int) -> np.ndarray:
	"""Merge connected components with area < min_area to neighboring dominant label.
	Strategy: for each label, get CCs; if small, reassign its pixels to the mode label in a 3x3 neighborhood of the original map.
	"""
	import cv2

	h, w = label_map.shape[:2]
	out = label_map.copy()
	unique_labels = np.unique(label_map)
	# Precompute padded map for neighborhood lookups
	pad = cv2.copyMakeBorder(out, 1, 1, 1, 1, cv2.BORDER_REPLICATE)

	for lbl in unique_labels.tolist():
		mask = (out == int(lbl)).astype(np.uint8)
		if mask.sum() == 0:
			continue
		num, comp, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
		for i in range(1, num):
			area = int(stats[i, cv2.CC_STAT_AREA])
			if area >= min_area:
				continue
			ys, xs = np.where(comp == i)
			# For each pixel in this micro component, choose the mode of 3x3 neighborhood in the original map
			for y, x in zip(ys, xs):
				y1, x1 = y + 1, x + 1
				nb = pad[y1-1:y1+2, x1-1:x1+2].ravel()
				# exclude current label to encourage merging
				nb = nb[nb != lbl]
				if nb.size == 0:
					continue
				# mode
				vals, counts = np.unique(nb, return_counts=True)
				out[y, x] = vals[np.argmax(counts)]
	return out


def outline_from_labels(label_map: np.ndarray, thickness: int = 2) -> np.ndarray:
	"""Generate outline mask from label boundaries (always closed).
	"""
	import cv2

	h, w = label_map.shape[:2]
	# Compute boundary by checking differences with shifted maps
	diff = np.zeros((h, w), dtype=np.uint8)
	diff |= (label_map != np.roll(label_map, 1, axis=0)).astype(np.uint8)
	diff |= (label_map != np.roll(label_map, -1, axis=0)).astype(np.uint8)
	diff |= (label_map != np.roll(label_map, 1, axis=1)).astype(np.uint8)
	diff |= (label_map != np.roll(label_map, -1, axis=1)).astype(np.uint8)
	edges = (diff > 0).astype(np.uint8) * 255
	if thickness > 1:
		k = max(1, thickness)
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
		edges = cv2.dilate(edges, kernel)
	return edges
