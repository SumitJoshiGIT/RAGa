from pydantic import BaseModel
from typing import Optional

class ImageMeta(BaseModel):
    resolution: Optional[str]
    format: Optional[str]

class TextMeta(BaseModel):
    author: Optional[str]
    language: Optional[str]
