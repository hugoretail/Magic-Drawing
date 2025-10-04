"""
Minimal pipeline — decode -> resize -> outline -> render worksheet.

This generates a basic "coloriage": white page with black outline of the photo.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np

from backend.ops.io import decode_image_bytes, pil_to_numpy_bgr, downscale_max_side, encode_png_base64
from backend.ops.outline import outline_edges
from backend.ops.render import compose_worksheet, draw_numbers, labels_viz, legend_viz, overlay_legend_on_worksheet
from backend.api.schemas import ConvertRequestOptions, ConvertResponse, ImageMeta
from backend.ops.quantize import quantize_bgr_kmeans
from backend.ops.segments import extract_regions, median_smooth_labels, merge_micro_regions, outline_from_labels
from backend.ops.placing import place_numbers


def convert_image_bytes_to_worksheet(data: bytes, opts: ConvertRequestOptions) -> ConvertResponse:
	#1) decode and convert to BGR
	pil = decode_image_bytes(data)
	img = pil_to_numpy_bgr(pil)
	#2) downscale to control runtime
	img = downscale_max_side(img, opts.max_size)
	h, w = img.shape[:2]

	#3) color quantization (preview)
	q_bgr, labels, palette = quantize_bgr_kmeans(img, max(2, min(24, opts.colors)))
	#3b) label smoothing + merge of micro-regions
	labels = median_smooth_labels(labels, ksize=3)
	labels = merge_micro_regions(labels, min_area=opts.merge_area)

	#4) outlines
	labels_edges = outline_from_labels(labels, thickness=opts.thickness)
	if (opts.outline_mode or "union").lower() == "union":
		canny_edges = outline_edges(img, thickness=opts.thickness)
		import cv2
		edges = cv2.bitwise_or(labels_edges, canny_edges)
	else:
		edges = labels_edges

	#5) render worksheet (white + outline)
	worksheet = compose_worksheet(edges, (h, w, 3))

	#6)regions and placement
	regions = extract_regions(labels, min_area=opts.min_area)
	places = place_numbers(regions)
	worksheet = draw_numbers(worksheet, places)

	#7)legend image and overlay
	legend_img = legend_viz(palette, box_size=32)
	worksheet_with_legend = overlay_legend_on_worksheet(worksheet, legend_img, margin=12, alpha=0.95)

	#8)pack response (with preview and optional labels viz)
	worksheet_png = encode_png_base64(worksheet_with_legend)
	preview_png = encode_png_base64(q_bgr) if opts.include_preview else None
	labels_img = labels_viz(labels, palette)
	labels_png = encode_png_base64(labels_img) if opts.include_preview else None
	legend_png = encode_png_base64(legend_img)
	meta = ImageMeta(width=w, height=h, colors=int(palette.shape[0]), num_regions=len(regions))
	return ConvertResponse(
		worksheet_png=worksheet_png,
		preview_png=preview_png,
		labels_png=labels_png,
		legend_png=legend_png,
		meta=meta,
	)
