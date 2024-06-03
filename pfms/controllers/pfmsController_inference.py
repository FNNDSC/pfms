from re import A
from fastapi import APIRouter, Query, Request, UploadFile

from fastapi.encoders import jsonable_encoder
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Callable, Any

import asyncio

from pydantic_core.core_schema import ExpectedSerializationTypes
from torch import parse_ir
from models import iresponse
import os
from datetime import datetime

import json
import pudb
from config import settings

from argparse import Namespace, ArgumentParser
import sys
from loguru import logger
import shutil

import tempfile
from pathlib import Path
import uuid
from uuid import UUID

from spleenseg import spleenseg as spleen
from spleenseg import splparser as psr
from starlette.responses import FileResponse

LOG = logger.debug

logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> │ "
    "<level>{level: <5}</level> │ "
    "<yellow>{name: >28}</yellow>::"
    "<cyan>{function: <30}</cyan> @"
    "<cyan>{line: <4}</cyan> ║ "
    "<level>{message}</level>"
)
logger.remove()
logger.opt(colors=True)
logger.add(sys.stderr, format=logger_format)
LOG = logger.info


def noop():
    """
    A dummy function that does nothing.
    """
    return {"status": True}


def modelLocation_get(modelName) -> Path:
    modelDir = settings.modelMeta.location / Path(modelName)
    fileLocation: Path = modelDir / "model.pth"
    return fileLocation


def inferenceDevice_get() -> str:
    if not settings.modelMeta.deviceState_read():
        settings.modelMeta.state_save()
    return settings.modelMeta.device


def inferenceDevice_set(device: str) -> iresponse.InferenceDevice:
    settings.modelMeta.device = device
    settings.modelMeta.state_save()
    iDevice: iresponse.InferenceDevice = iresponse.InferenceDevice()
    iDevice.device = device
    return iDevice


async def model_save(
    remote: UploadFile, modelName: str
) -> iresponse.ModelUploadResponse:
    modelUpload: iresponse.ModelUploadResponse = iresponse.ModelUploadResponse()
    modelLocation: Path = modelLocation_get(modelName)
    modelLocation.parent.mkdir(parents=True, exist_ok=True)
    with modelLocation.open("wb") as buffer:
        contents: bytes = await remote.read()
        buffer.write(contents)
    modelUpload.status = True
    modelUpload.message = f"model {modelName} saved successfully"
    modelUpload.location = modelLocation
    return modelUpload


def models_list() -> iresponse.ModelsAvailable:
    resp: iresponse.ModelsAvailable = iresponse.ModelsAvailable()
    try:
        resp.models = os.listdir(str(settings.modelMeta.location))
    except Exception as e:
        print(f"An exception in model listing was caught: {e}")
        print("This is probably safe and simply means no models have been POSTed.")
    return resp


def IOpaths_create() -> tuple[Path, Path]:
    sessionUUID: UUID = uuid.uuid4()
    now: datetime = datetime.now()
    nowstr: str = now.strftime("%Y-%m-%d-%H-%M-%S")
    baseParentPath: Path = (
        settings.analysisMeta.location / f"{nowstr}-{str(sessionUUID)}"
    )
    inputDir: Path = baseParentPath / "input"
    outputDir: Path = baseParentPath / "output"
    inputDir.mkdir(parents=True, exist_ok=True)
    outputDir.mkdir(parents=True, exist_ok=True)
    return inputDir, outputDir


def NIfTIvol_saveInput(remote: UploadFile, inputDir: Path) -> Path:
    saveDir: Path = inputDir / "imagesTs"
    saveDir.mkdir(parents=True, exist_ok=True)
    savePath: Path = saveDir / "input.nii.gz"
    with savePath.open("wb") as buffer:
        shutil.copyfileobj(remote.file, buffer)
    return savePath


def NIfTIvol_infer(remote: UploadFile, inputDir: Path, outputDir: Path) -> Path:
    NIfTIvol_saveInput(remote, inputDir)
    options: Namespace = psr.parser_interpret(psr.parser_setup(""), asModule=True)
    options.mode = "inference"
    options.device = settings.modelMeta.device
    options.logTransformVols = True
    options.inputdir = str(inputDir)
    options.outputdir = str(outputDir)
    spleen.main(options, inputDir, outputDir)
    outputFile: Path = outputDir / "inference" / "output.nii.gz"
    return outputFile


def model_prep(modelID: str, targetDir: Path):
    modelLocation: Path = modelLocation_get(modelID)
    shutil.copy(modelLocation, targetDir)


async def inferenceOnNIfTI(uploadFile: UploadFile, modelID: str = "") -> FileResponse:
    inputDir: Path
    outputDir: Path
    inputDir, outputDir = IOpaths_create()
    model_prep(modelID, inputDir)
    result: Path = NIfTIvol_infer(uploadFile, inputDir, outputDir)
    return FileResponse(
        path=result, media_type="application/octet-stream", filename="output.nii.gz"
    )
