#FastAPI APIRouter definitions (minimal object + comment-only examples)
from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
def health():
	"""Status liveness check."""
	return {"status": "ok"}

#note: Real endpoints (e.g., /magic/convert) will be added later.