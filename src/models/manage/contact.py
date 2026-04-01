"""Contact configuration model.

Maps to: manage/contacts/<slug>.toml
"""

from typing import Any

from pydantic import BaseModel


class ContactConfig(BaseModel):
    name: str
    slug: str
    phone: str = ""
    email: str = ""
    birthday: str = ""  # MM-DD format, e.g. "04-01"
    birth_year: int | None = None  # Optional, used to compute age
    relationship: str = ""
    info: dict[str, Any] = {}
