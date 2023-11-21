"""
    The starting point of the application.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .routers import http
from .models.shared import JSONException
from .models.api import HTTPResponse

# Webserver
app = FastAPI(
    title="Digitiamo Curl-as-a-Service Test",
    description="Evaluation test for Digitiamo S.r.l",
    version="1.0.0",
    contact={
        "name": "Tommaso Ventafridda",
        "url": "https://github.com/tomventa/digitiamo-test",
    },
)

app.include_router(http.router)


@app.exception_handler(JSONException)
async def custom_exception_handler(_: Request, exc: JSONException) -> JSONResponse:
    """Handle exceptions for the /api/HTTP endpoint logic

    Args:
        request (Request): The request object.
        exc (JSONException): The exception to handle.

    Returns:
        JSONResponse: JSON response with the exception details.
    """
    ret = HTTPResponse(
        status = 500,
        errors = {
            "id": exc.id,
            "detail": exc.detail
        },
        data = None
    )
    return JSONResponse(status_code=500, content=ret.model_dump(by_alias=True))
