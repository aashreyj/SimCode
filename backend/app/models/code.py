from typing import Optional

from pydantic import BaseModel


class Code(BaseModel):
    language: str
    prerequisites: Optional[str] = ""
    code: str
