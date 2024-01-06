from typing import Optional, List
from pydantic import BaseModel

class Article(BaseModel):
    data: Optional[List] = []

