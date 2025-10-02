"""
I/O helpers: validate, decode and convert images between Pillow and NumPy:
"""

from __future__ import annotations

import base64
from io import BytesIO
from typing import Tuple

import numpy as np
from PIL import Image, ImageOps, ImageFile, UnidentifiedImageError

# Allow loading truncated JPEGs
ImageFile.LOAD_TRUNCATED_IMAGES = True


def decode_image_bytes(data: bytes, *, max_bytes: int = 50 * 1024 * 1024) -> Image.Image:
	"""Decode bytes into a PIL RGB image and apply EXIF orientation.

	Raises ValueError on invalid data.
	"""
	if not data:
		raise ValueError("No data received")
	if len(data) > max_bytes:
		raise ValueError("File too large. Please upload an image under 50 MB.")
	# First attempt: Pillow
	try:
		img = Image.open(BytesIO(data))
		img = ImageOps.exif_transpose(img)
		if img.mode != "RGB":
			img = img.convert("RGB")
		return img
	except UnidentifiedImageError as e:
		# Fallback: OpenCV imdecode (handles some edge cases)
		try:
			import cv2  # lazy
			arr = np.frombuffer(data, dtype=np.uint8)
			bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
			if bgr is None:
				raise ValueError("Could not decode image (cv2 returned None)")
			# Convert BGR -> RGB and back into PIL for consistent pipeline
			rgb = bgr[..., ::-1]
			return Image.fromarray(rgb)
		except Exception as ee:
			raise ValueError(f"Invalid image data (Pillow+OpenCV failed): {ee}")
	except Exception as e:
		raise ValueError(f"Invalid image data: {e}")


def pil_to_numpy_bgr(img: Image.Image) -> np.ndarray:
	"""Convert PIL (RGB) to NumPy BGR uint8."""
	arr = np.asarray(img)  #RGB
	if arr.ndim == 2:  #grayscale
		arr = np.stack([arr, arr, arr], axis=-1)
	#RGB -> BGR
	return arr[..., ::-1].copy()


def downscale_max_side(img_bgr: np.ndarray, max_side: int) -> np.ndarray:
	"""Downscale to ensure max(height, width) <= max_side, keep aspect ratio."""
	h, w = img_bgr.shape[:2]
	scale = min(1.0, float(max_side) / float(max(h, w)))
	if scale >= 0.999:
		return img_bgr
	new_w = max(1, int(round(w * scale)))
	new_h = max(1, int(round(h * scale)))
	import cv2

	return cv2.resize(img_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)


def encode_png_base64(img: np.ndarray) -> str:
	"""Encode BGR/RGB/Gray image to base64-encoded PNG string."""
	import cv2

	if img.ndim == 3 and img.shape[2] == 3:
		bgr = img
	elif img.ndim == 2:
		bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
	else:
		raise ValueError("Unsupported image shape for PNG encoding")

	ok, buf = cv2.imencode(".png", bgr)
	if not ok:
		raise RuntimeError("PNG encoding failed")
	return base64.b64encode(buf.tobytes()).decode("ascii")
