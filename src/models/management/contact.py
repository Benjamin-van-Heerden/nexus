"""Contact configuration model.

Maps to: management/contacts/<slug>.toml
"""

from datetime import date
from typing import Any

from pydantic import BaseModel


class ContactConfig(BaseModel):
    name: str
    slug: str
    phone: str = ""
    email: str = ""
    birthday: date | None = None
    relationship: str = ""
    info: dict[str, Any] = {}
