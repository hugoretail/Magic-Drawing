"""
Pydantic models for requests/responses

Notes on defaults and ranges we enforce:
- colors: default 9 (typical for kid-friendly worksheets), 2..24 allowed
- max_size: default 1024 (downscale for performance), 128..4096 allowed
- thickness: default 2, 1..10 allowed
- min_area: default 80 px^2 to skip tiny noisy regions, 1..10000 allowed
- include_preview: default True
- return_pdf: default False (enable later when PDF support is added)
"""

from __future__ import annotations
	
from typing import Optional, Annotated
from typing import Literal
from pydantic import BaseModel, Field

#just to list the classes
__all__ = [
	"ConvertRequestOptions",
	"ImageMeta",
	"ConvertResponse",
]


class ConvertRequestOptions(BaseModel):
	"""Options provided with the uploaded image."""

	colors: Annotated[int, Field(9, ge=2, le=24, description="Number of color clusters to quantize to.")]
	max_size: Annotated[int, Field(1024, ge=128, le=4096, description="Max image side after downscaling to control runtime and memory.")]
	thickness: Annotated[int, Field(2, ge=1, le=10, description="Outline thickness in pixels.")]
	min_area: Annotated[int, Field(80, ge=1, le=10000, description="Minimum region area in px^2 to receive a number.")]
	merge_area: Annotated[int, Field(200, ge=1, le=100000, description="Minimum area (px^2) to keep as a standalone region; smaller connected components will be merged into a neighboring label before numbering.")]
	outline_mode: Annotated[str, Field("union", description="Outline generation strategy: 'labels' for only label boundaries, or 'union' for union(labels, canny).")]
	include_preview: bool = Field(True, description="Include color preview image in response.")
	return_pdf: bool = Field(False, description="Also return a PDF (if supported/enabled).")


class ImageMeta(BaseModel):
	width: int = Field(..., ge=1)
	height: int = Field(..., ge=1)
	colors: int = Field(..., ge=1)
	num_regions: int = Field(..., ge=0)


class ConvertResponse(BaseModel):
	"""
  Response payload for the conversion endpoint.
	Images are base64-encoded PNGs, so the frontend can easily render or download them.
	"""

	worksheet_png: str = Field(..., description="Base64-encoded PNG of the worksheet (numbers + outline).")
	preview_png: Optional[str] = Field(None, description="Base64-encoded PNG of the quantized preview (optional).")
	labels_png: Optional[str] = Field(None, description="Base64-encoded PNG of the label map (optional/debug).")
	meta: ImageMeta


