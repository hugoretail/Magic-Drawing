"""
Minimal pipeline — decode -> resize -> outline -> render worksheet.

This generates a basic "coloriage": white page with black outline of the photo.
Later steps will add quantization, labels, numbers and legend.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np

from backend.ops.io import decode_image_bytes, pil_to_numpy_bgr, downscale_max_side, encode_png_base64
from backend.ops.outline import outline_edges
from backend.ops.render import compose_worksheet
from backend.api.schemas import ConvertRequestOptions, ConvertResponse, ImageMeta
from backend.ops.quantize import quantize_bgr_kmeans


def convert_image_bytes_to_worksheet(data: bytes, opts: ConvertRequestOptions) -> ConvertResponse:
	#1) decode and convert to BGR
	pil = decode_image_bytes(data)
	img = pil_to_numpy_bgr(pil)
	#2) downscale to control runtime
	img = downscale_max_side(img, opts.max_size)
	h, w = img.shape[:2]

	#3) color quantization (preview)
	q_bgr, labels, palette = quantize_bgr_kmeans(img, max(2, min(24, opts.colors)))

	#4) outline detection
	edges = outline_edges(img, thickness=opts.thickness)

	#5) render worksheet
	worksheet = compose_worksheet(edges, (h, w, 3))

	#6)pack response (with preview)
	worksheet_png = encode_png_base64(worksheet)
	preview_png = encode_png_base64(q_bgr) if opts.include_preview else None
	labels_png = None
	meta = ImageMeta(width=w, height=h, colors=int(palette.shape[0]), num_regions=0)
	return ConvertResponse(
		worksheet_png=worksheet_png,
		preview_png=preview_png,
		labels_png=labels_png,
		meta=meta,
	)
