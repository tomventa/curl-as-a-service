"""HTTP router for the API. This is where the API endpoints are defined for the HTTP module."""

from uuid import uuid4
from pydantic import UUID4
from fastapi import APIRouter, Depends
from pymongo.collection import Collection
from app.models.api import ServerSideURL
from app.models.database import RequestModel
from app.models.shared import JSONException
from app.utils import url_info, make_request
from app.database import get_db


router = APIRouter(prefix="/api/HTTP", tags=["http"])


@router.post("/{method}", response_model=RequestModel)
def perform_a_request(url: ServerSideURL, method: str, db = Depends(get_db)):
    """Perform a HTTP request to the given URL using the given method."""
    # Make the request, see utils.py
    response_and_request = make_request(url.url, method, [], [], 0)
    # Decompose the URL, see models/api.py
    url_analysis = {'url': url_info(url.url)}
    # If there are no errors, merge the URL analysis with the response and request data
    if response_and_request['errors'] is None:
        response_and_request['data'] = url_analysis | response_and_request['data']
    # Insert the response and request data into the database
    new_record = RequestModel(**response_and_request | {'_id': str(uuid4())})
    result_collection: Collection[RequestModel] = db.results
    result_collection.insert_one(new_record.model_dump(by_alias=True))
    return new_record

@router.get("/{uid}", response_model=RequestModel)
def view_a_request(uid: UUID4, db = Depends(get_db)):
    """View a request by its UUID."""
    result_collection: Collection[RequestModel] = db.results
    result = result_collection.find_one({'_id': str(uid)})
    if result is None:
        #raise HTTPException(status_code=404, detail="Request not found")
        raise JSONException(
                id='ID_NOT_FOUND',
                detail='The requested UUID was not found in the database'
            )
    return RequestModel(**result)
