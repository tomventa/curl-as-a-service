from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, constr

class ServerSideURL(BaseModel):
    url: str = Field(example="https://www.google.com/")

class ServerSideURLDecomposed(ServerSideURL):
    protocol: str = Field(example="https")
    domain: str = Field(example="www.google.com")
    path: str = Field(example="/")

class Header(BaseModel):
    name: str = Field(example="Content-Type")
    value: str = Field(example="application/json")

class ServerSideResponse(BaseModel):
    http_version: str = Field(example="HTTP/1.1")
    status_code: int = Field(example=200)
    headers: dict # List[Header]

class ServerSideRequest(BaseModel):
    method: str = Field(example="GET")
    url: str = Field(example="https://www.google.com/")

class HTTPResponseData(BaseModel):
    url: ServerSideURLDecomposed
    response: List[ServerSideResponse]
    request: List[ServerSideRequest]

class HTTPResponseErrors(BaseModel):
    id: str = Field(example="TOO_MANY_REDIRECTS")
    detail: str = Field(example="Too many redirects while following the url you provided")


class HTTPResponse(BaseModel):
    status: int
    errors: HTTPResponseErrors | None
    data: HTTPResponseData | None

