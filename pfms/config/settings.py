import os
from typing import Any, ClassVar, Type
from pydantic import AnyHttpUrl, AnyUrl
from pydantic_settings import BaseSettings
from pathlib import Path
import platformdirs as pfd
import json
import pudb


class AppData(BaseSettings):
    appName: str = "pfms"
    appAuthor: str = "FNNDSC"
    appConfigDir: Path = Path(pfd.user_config_dir(appName))
    appModelDataFile: Path = Path("modelMeta.json")
    appModelDataFP: Path = appConfigDir / appModelDataFile

    def initialize(self):
        # pudb.set_trace()
        if not self.appConfigDir.exists():
            self.appConfigDir.mkdir(parents=True, exist_ok=True)


class ModelMeta(BaseSettings):
    location: Path = Path.home() / "spleenseg" / "models"
    device: str = "cuda:0"
    modelAppData: AppData = AppData()

    @classmethod
    def from_dict(cls: type["ModelMeta"], configDict: dict[str, Any]) -> "ModelMeta":
        return cls(**configDict)

    def state_save(self):
        with self.modelAppData.appModelDataFP.open("w") as f:
            json.dump({"location": str(self.location), "device": self.device}, f)

    def deviceState_read(self) -> bool:
        if not self.modelAppData.appModelDataFP.exists():
            return False
        with open(self.modelAppData.appModelDataFP) as f:
            fileData = json.load(f)
            self.device = fileData["device"]
            return True

    def initialize(self, appData: AppData = AppData()):
        self.modelAppData = appData
        self.deviceState_read()


class AnalysisMeta(BaseSettings):
    location: Path = Path.home() / "spleenseg" / "analysis"


class Vault(BaseSettings):
    locked: bool = False
    vaultKey: str = ""


class Credentials(BaseSettings):
    username: str = "chris"
    password: str = "chris1234"


def vaultCheckLock(vault: Vault) -> None:
    if vault.vaultKey and not vault.locked:
        vault.locked = True
        print("Vault check: key has already been set. Vault is now LOCKED.")


# pudb.set_trace()
vault = Vault()
appData = AppData()
appData.initialize()
modelMeta = ModelMeta()
modelMeta.initialize(appData)
analysisMeta = AnalysisMeta()
