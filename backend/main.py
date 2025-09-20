"""FastAPI entrypoint.

This file supports two run modes:
- Imported as a module (preferred): `uvicorn backend.main:app --reload`
- Executed directly (dev convenience): `python backend/main.py`

When executed directly, we add the project root to sys.path so that
`from backend.api.routes import router` resolves correctly.
"""

import os
import sys
from pathlib import Path

if __package__ in (None, ""):
  ROOT = str(Path(__file__).resolve().parents[1])
  if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

#note: Uvicorn discovers the app through the "backend.main:app" syntax
#meaning is that it's looking for the "app" object in "backend.main"
from backend.api.routes import router

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"], #allow all origins
  allow_methods=["*"], #allow all methods (GET,POST,...)
  allow_headers=["*"], #allow all headers
)

app.include_router(router) #inlucde the router in the app, litteraly

#dev mode: simple way to execute main.py
if __name__ == "__main__":
  try:
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
  except Exception as e:
    print(f"Failed to start dev server: {e}")
