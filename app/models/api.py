from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, constr

class ServerSideURL(BaseModel):
    url: str = Field(examples=["https://www.google.com/"])

class ServerSideURLDecomposed(ServerSideURL):
    protocol: str = Field(examples=["https"])
    domain: str = Field(examples=["www.google.com"])
    path: str = Field(examples=["/"])

class Header(BaseModel):
    name: str = Field(examples=["Content-Type"])
    value: str = Field(examples=["application/json"])

class ServerSideResponse(BaseModel):
    http_version: str = Field(examples=["HTTP/1.1"])
    status_code: int = Field(examples=[200])
    headers: dict # List[Header]

class ServerSideRequest(BaseModel):
    method: str = Field(examples=["GET"])
    url: str = Field(examples=["https://www.google.com/"])

class HTTPResponseData(BaseModel):
    url: ServerSideURLDecomposed
    response: List[ServerSideResponse]
    request: List[ServerSideRequest]

class HTTPResponseErrors(BaseModel):
    id: str = Field(examples=["TOO_MANY_REDIRECTS"])
    detail: str = Field(examples=["Too many redirects while following the url you provided"])


class HTTPResponse(BaseModel):
    status: int
    errors: HTTPResponseErrors | None
    data: HTTPResponseData | None

