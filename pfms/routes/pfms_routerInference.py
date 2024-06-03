from shutil import ignore_patterns
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks, Request
from fastapi import File, UploadFile, Path, Form
from typing import List, Dict, Any, Union, Annotated

from starlette.responses import FileResponse

from models import credentialModel
from models import iresponse
from controllers import pfmsController_inference
from routes import credentialRouter
from pathlib import Path as PathLib
from config import settings
from pftag import pftag
import pudb

router = APIRouter()
router.tags = ["pfms endpoints"]


@router.get(
    "/spleenseg/inference/device/",
    response_model=iresponse.InferenceDevice,
    summary="""
    GET the current inference device hardware.
    """,
)
def device_list() -> iresponse.InferenceDevice:
    """
    Description
    -----------

    GET the current device assigned to the pfms server.

    Returns
    -------
    * `iresponse.InferenceDevice`: The response containing the inference device
    """
    # pudb.set_trace()
    iDevice: iresponse.InferenceDevice = iresponse.InferenceDevice()
    iDevice.device = pfmsController_inference.inferenceDevice_get()
    return iDevice


@router.put(
    "/spleenseg/inference/device/{device}",
    response_model=iresponse.InferenceDevice,
    summary="""
    PUT the inference device hardware to use.
    """,
)
def device_put(
    device: str, iDevice: iresponse.InferenceDevice
) -> iresponse.InferenceDevice:
    """
    Description
    -----------

    PUT the inference device to use.

    Returns
    -------
    * `iresponse.InferenceDevice`: The response containing the inference device
    """
    # pudb.set_trace()
    return pfmsController_inference.inferenceDevice_set(device)


@router.get(
    "/spleenseg/modelpth/",
    response_model=iresponse.ModelsAvailable,
    summary="""
    GET the list of available models.
    """,
)
def models_listAll() -> iresponse.ModelsAvailable:
    """
    Description
    -----------

    GET the current list of models in the pfms server.

    Returns
    -------
    * `iresponse.ModelsAvailable`: The response containing the list of models
    """
    # pudb.set_trace()
    modelList: iresponse.ModelsAvailable = pfmsController_inference.models_list()
    return modelList


@router.post(
    "/spleenseg/modelpth/",
    response_model=iresponse.ModelUploadResponse,
    summary="""
    POST a model pth file to the server.
    """,
)
async def model_upload(
    request: Request,
    file: UploadFile = File(...),
) -> iresponse.ModelUploadResponse:
    """
    Description
    -----------

    POST (upload) a model weights file. Pass a query parameter of `?modelID=<modelID>`
    to set the internal name of this model.

    Returns
    -------
    * `iresponse.ModelUploadResponse`: The response containing the list of available
       models.
    """
    # pudb.set_trace()
    modelID: str = request.query_params.get("modelID", "")
    modelUpload: iresponse.ModelUploadResponse = (
        await pfmsController_inference.model_save(file, modelID)
    )
    return modelUpload


@router.post(
    "/spleenseg/NIfTIinference/",
    summary="""
        POST (upload) a NIfTI volume. Pass a query parameter of `?modelID=<modelID>`
        to set the internal name of the model to use for inference. Returns a
        `FileResponse` octet-stream of the generated segmentned NIfTI volume
        response.
    """,
)
async def uploadAndInferOnNIfTIfile(
    request: Request,
    file: UploadFile = File(...),
) -> FileResponse:
    """
    Description
    -----------

    POST a NIfTI volume spleen scan, specify a modelID in query params,
    and expect a reponse inference.

    Returns
    -------
    * `FileResponse`: The response from the inference as an octet-stream; save
    to compressed NIfTI file.
    """
    # pudb.set_trace()
    modelID: str = request.query_params.get("modelID", "")
    inference: FileResponse = await pfmsController_inference.inferenceOnNIfTI(
        file, modelID
    )
    return inference
