from typing import Optional
import logging

from fastapi import APIRouter, File, UploadFile, HTTPException, Query

from backend.api.schemas import ConvertRequestOptions, ConvertResponse
from backend.services.magic import convert_image_bytes_to_worksheet


router = APIRouter()


@router.get("/health")
def health():
	"""Status liveness check."""
	return {"status": "ok"}


@router.post("/magic/convert", response_model=ConvertResponse)
async def magic_convert(
	file: UploadFile = File(..., description="Input image file (jpg/png/webp)."),
	colors: int = Query(9, ge=2, le=24),
	max_size: int = Query(1024, ge=128, le=4096),
	thickness: int = Query(2, ge=1, le=10),
	min_area: int = Query(80, ge=1, le=10000),
	include_preview: bool = Query(True),
	return_pdf: bool = Query(False),
):
	try:
		data = await file.read()
		if not data:
			raise ValueError("Empty file upload. Please choose an image file.")
		if not data:
			raise ValueError("Empty file upload. Please choose an image file.")
		opts = ConvertRequestOptions(
			colors=colors,
			max_size=max_size,
			thickness=thickness,
			min_area=min_area,
			include_preview=include_preview,
			return_pdf=return_pdf,
		)
		result = convert_image_bytes_to_worksheet(data, opts)
		return result
	except Exception as e:
		logging.exception("/magic/convert failed: %s", e)
		raise HTTPException(status_code=400, detail=str(e))
