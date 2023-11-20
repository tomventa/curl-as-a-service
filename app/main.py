from fastapi import FastAPI, Depends, Request, Query
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
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
async def unicorn_exception_handler(request: Request, exc: JSONException):
    ret = HTTPResponse(
        status = 500,
        errors = {
            "id": exc.id,
            "detail": exc.detail
        },
        data = None
    )
    return JSONResponse(status_code=500, content=ret.model_dump(by_alias=True))

# Serve static files
app.mount('/', StaticFiles(directory='app/static/'), name='static')
