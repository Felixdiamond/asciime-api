from pydantic import BaseModel, Field
from typing import List, Optional, Union

class GifResponse(BaseModel):
    id: str
    url: str
    size: Optional[int] = None
    dims: Optional[List[Optional[int]]] = None
    source: str
    category: str

class BatchResponse(BaseModel):
    success: bool
    data: List[GifResponse]
    error: Optional[str] = None

class RandomResponse(BaseModel):
    success: bool
    data: Optional[GifResponse] = None
    error: Optional[str] = None

class Category(BaseModel):
    id: str
    terms: List[str]
    subreddits: List[str]

class CategoriesResponse(BaseModel):
    success: bool
    data: List[Category]