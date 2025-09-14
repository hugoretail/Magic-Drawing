from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"], #allow all origins
  allow_methods=["*"], #allow all methods (GET,POST,...)
  allow_header=["*"], #allow all headers
)

