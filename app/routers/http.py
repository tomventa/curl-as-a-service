from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Body
import json
from app.models.api import ServerSideURL, HTTPResponse, ServerSideURLDecomposed
from app.models.database import MongoBaseModel, RequestModel
from uuid import UUID, uuid4
from pydantic import UUID4
import requests
from app.utils import url_info, make_request
from app.database import get_db
from pymongo.collection import Collection


router = APIRouter(prefix="/api/HTTP", tags=["http"])


@router.post("/{method}", response_model=RequestModel)
def perform_a_request(URL: ServerSideURL, method: str, request: Request, db = Depends(get_db)):
    # Make the request, see utils.py
    response_and_request = make_request(URL.url, method, [], [], 0)
    # Decompose the URL, see models/api.py
    url_analysis = {'url': url_info(URL.url)}
    # If there are no errors, merge the URL analysis with the response and request data
    if response_and_request['errors'] is None:
        response_and_request['data'] = url_analysis | response_and_request['data']
    # 
    new_record = RequestModel(**response_and_request | {'_id': str(uuid4())})
    result_collection: Collection[RequestModel] = db.results
    result_collection.insert_one(new_record.dict(by_alias=True))
    return new_record

@router.get("/{id}", response_model=RequestModel)
def view_a_request(id: UUID4, db = Depends(get_db)):
    result_collection: Collection[RequestModel] = db.results
    result = result_collection.find_one({'_id': str(id)})
    if result is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return RequestModel(**result)
