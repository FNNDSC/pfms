from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel
import pudb
from config import settings
from fastapi import File, UploadFile


class InferenceResponseNIFTI(BaseModel):
    inputfilename: str = ""
    shape: list[int] = []
    dtype: str = ""
    data: list[float] = []


class ModelsAvailable(BaseModel):
    models: list[str] = []


class ModelUploadResponse(BaseModel):
    status: bool = False
    message: str = ""
    location: Path = Path("")


class InferenceDevice(BaseModel):
    device: str = ""


class ModelUploadRequest(BaseModel):
    identifier: str
    file: UploadFile = File(...)
