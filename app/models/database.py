"""Database models for the application."""

from typing import Optional
from pydantic import BaseModel, Field
from app.models.api import HTTPResponse

class MongoBaseModel(BaseModel):
    """Base model for all models that are stored in mongodb."""
    id: Optional[str] = Field(
        alias="_id",
        description="Unique identifier for the object when stored in mongodb"
      )

    class ConfigDict:
        """Pydantic configuration for the model."""
        populate_by_name = True
        arbitrary_types_allowed = True

class RequestModel(MongoBaseModel, HTTPResponse):
    """Model for the HTTP request object.
    Based on models/api HTTPResponse model +
    id: Unique identifier for the object when stored in mongodb
    """
