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
