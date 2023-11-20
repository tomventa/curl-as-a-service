import json
import pytest
from unittest import mock
from app.utils import url_info, detect_ssrf, resolve_ip, make_request
from app.models.shared import JSONException

def test_http_post(client):
    response = client.post(
        "/api/HTTP/GET",
        json={
            "url": "https://blog.tomh.it/"
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == 200
    assert response.json()["errors"] is None


def test_api_google_mock_200(client):
    with mock.patch('app.utils.detect_ssrf') as mock_detect_ssrf, \
         mock.patch('app.utils.requests') as mock_requests:
        mock_detect_ssrf.return_value = False

        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.is_redirect = False
        mock_response.raw.version = 11
        mock_response.headers = {
            "Content-Type": "text/html",
            "Content-Length": "123",
            "Date": "Mon, 18 Oct 2021 14:00:00 GMT",
            "Server": "Apache 19/1.2",
        }

        mock_requests.request.return_value = mock_response

        response = client.post(
            "/api/HTTP/GET",
            json={
                "url": "https://www.google.it/"
            }
        )
        assert response.status_code == 200
        assert response.json()["status"] == 200
        assert response.json()["errors"] is None
        assert response.json()["data"]["response"][0]["status_code"] == 200
        assert len(response.json()["data"]["response"][0]["headers"]) > 0
        assert response.json()["data"]["response"][0]["headers"]["Content-Type"] == "text/html"
        assert response.json()["data"]["response"][0]["headers"]["Content-Length"] == "123"


def test_api_google_mock_302_infinite_redirect(client):
    with mock.patch('app.utils.detect_ssrf') as mock_detect_ssrf, \
         mock.patch('app.utils.requests') as mock_requests:
        mock_detect_ssrf.return_value = False

        mock_response = mock.MagicMock()
        mock_response.status_code = 302
        mock_response.is_redirect = True
        mock_response.raw.version = 11
        mock_response.headers = {
            "Content-Type": "text/html",
            "Content-Length": "123",
            "Date": "Mon, 18 Oct 2021 14:00:00 GMT",
            "Server": "Apache 19/1.2",
            "Location": "https://www.google.it/"
        }

        mock_requests.request.return_value = mock_response

        response = client.post(
            "/api/HTTP/GET",
            json={
                "url": "https://www.google.it/"
            }
        )
        assert response.status_code == 500
        assert response.json()["status"] == 500
        assert response.json()["errors"] is not None
        assert response.json()["errors"]["id"] == "TOO_MANY_REDIRECTS"


def test_api_google_mock_302_single_redirect(client):
    with mock.patch('app.utils.detect_ssrf') as mock_detect_ssrf, \
         mock.patch('app.utils.requests') as mock_requests:
        mock_detect_ssrf.return_value = False
        
        def mocked_requests_get(*args, **kwargs):
            if args[1] == "https://first.google.com":
                mock_response = mock.MagicMock()
                mock_response.status_code = 302
                mock_response.is_redirect = True
                mock_response.raw.version = 11
                mock_response.headers = {
                    "Content-Type": "text/html",
                    "Content-Length": "123",
                    "Date": "Mon, 18 Oct 2021 14:00:00 GMT",
                    "Server": "Apache 2/1.20",
                    "Location": "https://second.google.com"
                }
                return mock_response
            elif args[1] == "https://second.google.com":
                mock_response = mock.MagicMock()
                mock_response.status_code = 200
                mock_response.is_redirect = False
                mock_response.raw.version = 11
                mock_response.headers = {
                    "Content-Type": "text/html",
                    "Content-Length": "123",
                    "Date": "Mon, 18 Oct 2021 14:00:01 GMT",
                    "Server": "Nginx 1.2",
                }
                return mock_response


        mock_requests.request.side_effect = mocked_requests_get

        response = client.post(
            "/api/HTTP/GET",
            json={
                "url": "https://first.google.com"
            }
        )
        assert response.status_code == 200
        assert response.json()["status"] == 200
        assert response.json()["errors"] is None
        assert response.json()["data"]["response"][0]["status_code"] == 302
        assert response.json()["data"]["response"][1]["status_code"] == 200

def test_api_google_mock_302_single_redirect_ssrf(client):
    with mock.patch('app.utils.requests') as mock_requests, \
         mock.patch('app.utils.socket.gethostbyname') as mock_gethostbyname:

        def mocked_get_host_by_name(*args, **kwargs):
            if args[0] == "first.google.com":
                return "123.1.2.3"
            elif args[0] == "second.google.com":
                return "127.0.0.1"
        
        def mocked_requests_get(*args, **kwargs):
            if args[1] == "https://first.google.com":
                mock_response = mock.MagicMock()
                mock_response.status_code = 302
                mock_response.is_redirect = True
                mock_response.raw.version = 11
                mock_response.headers = {
                    "Content-Type": "text/html",
                    "Content-Length": "123",
                    "Date": "Mon, 18 Oct 2021 14:00:00 GMT",
                    "Server": "Apache 2/1.20",
                    "Location": "https://second.google.com"
                }
                return mock_response
            elif args[1] == "https://second.google.com":
                mock_response = mock.MagicMock()
                mock_response.status_code = 200
                mock_response.is_redirect = False
                mock_response.raw.version = 11
                mock_response.headers = {
                    "Content-Type": "text/html",
                    "Content-Length": "123",
                    "Date": "Mon, 18 Oct 2021 14:00:01 GMT",
                    "Server": "Nginx 1.2",
                }
                return mock_response


        mock_gethostbyname.side_effect = mocked_get_host_by_name
        mock_requests.request.side_effect = mocked_requests_get

        response = client.post(
            "/api/HTTP/GET",
            json={
                "url": "https://first.google.com"
            }
        )
        assert response.status_code == 500
        assert response.json()["status"] == 500
        assert response.json()["errors"] is not None
        assert response.json()["errors"]["id"] == "SSRF_DETECTED"
