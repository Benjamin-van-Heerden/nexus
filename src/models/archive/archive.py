"""Archive configuration and state models.

Maps to: archive/archive.toml and archive/state.toml
"""

from datetime import datetime

from pydantic import BaseModel


class MaintenanceConfig(BaseModel):
    staleness_days: int = 90
    batch_size: int = 10


class QmdConfig(BaseModel):
    collection_name: str = "nexus-archive"
    default_recall_n: int = 10


class ArchiveConfig(BaseModel):
    interests: list[str] = []
    maintenance: MaintenanceConfig = MaintenanceConfig()
    qmd: QmdConfig = QmdConfig()


class RenameRecord(BaseModel):
    old: str
    new: str
    at: datetime


class ArchiveState(BaseModel):
    last_reindex: datetime | None = None
    last_qmd_update: datetime | None = None
    schema_version: int = 1
    pending_qmd_update: bool = False
    renames: list[RenameRecord] = []
