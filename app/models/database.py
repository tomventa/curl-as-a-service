from typing import List, Optional
from click import option
from pydantic import BaseModel, Field, HttpUrl, UUID4
from .api import HTTPResponse, HTTPResponseData
from uuid import uuid4

class MongoBaseModel(BaseModel):
  id: Optional[str] = Field(optional=True, alias="_id", description="Unique identifier for the object when stored in mongodb")
  class Config:
      allow_population_by_field_name = True
      arbitrary_types_allowed = True

class RequestModel(MongoBaseModel, HTTPResponse):
    pass