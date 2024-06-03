from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from base.router import helloRouter_create

from routes.pfms_routerInference import router as pfms_routerInference
from routes.credentialRouter import router as credential_router
from os import path
from config import settings
import pudb

with open(path.join(path.dirname(path.abspath(__file__)), "ABOUT")) as f:
    str_about: str = f.read()

with open(path.join(path.dirname(path.abspath(__file__)), "VERSION")) as f:
    str_version: str = f.read().strip()

tags_metadata: list = [
    {
        "name": "pfms endpoints",
        "description": """
            Endpoints for uploading models and performing inference on a variety
            of inputs. The most common upload type is a NIfTI volume, with the
            return volume also being NIfTI.
            """,
    },
    {
        "name": "Credentialling services",
        "description": """
            Provide API endpoints for setting a vaultKey which is used to unlock
            sensitive data.
            """,
    },
    {
        "name": "pfms environmental detail",
        "description": """
            Provide API GET endpoints that provide information about the
            service itself and the compute environment in which the service
            is deployed.
            """,
    },
]

# On startup, check if a vaultKey has been set by the environment,
# and if so, check/lock the vault.
settings.vaultCheckLock(settings.vault)

app = FastAPI(title="pfms", version=str_version, openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"],
)

hello_router: APIRouter = helloRouter_create(
    name="pfms_hello", version=str_version, about=str_about
)

app.include_router(pfms_routerInference, prefix="/api/v1")

app.include_router(credential_router, prefix="/api/v1")

app.include_router(hello_router, prefix="/api/v1")
