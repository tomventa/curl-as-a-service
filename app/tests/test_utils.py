"""Test for utils module in app/utils.py"""

from unittest import mock
import pytest
from app.utils import url_info, detect_ssrf, resolve_ip, make_request
from app.models.shared import JSONException

def test_url_info():
    """Test url_info function from utils.py module"""
    assert url_info("https://www.google.com/test") == {
        "url": "https://www.google.com/test",
        "protocol": "https",
        "domain": "www.google.com",
        "path": "/test"
    }

    with pytest.raises(JSONException):
        url_info("http://[2001::2/124]/]")


def test_resolve_ip():
    """Test resolve_ip function from utils.py module
    
        First test: Test if raises JSONException when the domain is unresolvable
        Second test: Test if returns the correct IP address when the domain is resolvable
    """
    with pytest.raises(JSONException):
        resolve_ip("this.does.not.exists@")

    with mock.patch('app.utils.socket') as mock_socket:
        # Mock the gethostbyname function to return a valid IP address
        mock_socket.gethostbyname.return_value = '192.168.0.1'

        # Test with a valid IP address input
        assert resolve_ip('192.168.0.1') == '192.168.0.1'

        # Test with a valid domain input
        assert resolve_ip('example.com') == '192.168.0.1'


def test_detect_ssrf():
    """Test detect_ssrf function from utils.py module
    
        First test: Test if returns True when the domain is pointing to a private IP address
        Second test: Test if returns False when the domain is not pointing to a private IP address
    """
    with mock.patch('app.utils.socket') as mock_socket:
        # Url is a local IP address
        mock_socket.gethostbyname.return_value = '127.0.0.1'
        assert detect_ssrf('http://example.com') is True

        # Url is not a local IP address
        mock_socket.gethostbyname.return_value = '123.123.123.123'
        assert detect_ssrf('http://example.com') is False


@pytest.mark.parametrize("ssrf_cases", [
        "127.0.0.1", 
        "127.1.2.3", 
        "255.255.255.1", 
        "192.168.1.1"
        "0", "::", "0.0.0.0", "::1",
        "0:0:0:0:0:FFFF:7F00:0001",
    ])
def test_detect_ssrf_true(ssrf_cases):
    """Test detect_ssrf function from utils.py module

        Test a list of possible private IP address / loopback address
    """
    with mock.patch('app.utils.socket') as mock_socket:
        mock_socket.gethostbyname.return_value = ssrf_cases
        assert detect_ssrf('http://example.com') is True


@pytest.mark.parametrize("ssrf_cases", [
        "54.0.1.2",
        "123.1.2.3",
        "8.8.8.8"
    ])
def test_detect_ssrf_false(ssrf_cases):
    """Test detect_ssrf function from utils.py module
    
        Test a list of possible public IP address
    """
    with mock.patch('app.utils.socket') as mock_socket:
        mock_socket.gethostbyname.return_value = ssrf_cases
        assert detect_ssrf('http://example.com') is False


def test_make_request():
    """Test make_request function from utils.py module
    
        Test if returns the correct response when the request is successful
    """
    with mock.patch('app.utils.detect_ssrf') as mock_detect_ssrf, \
         mock.patch('app.utils.requests') as mock_requests:
        mock_detect_ssrf.return_value = False

        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.is_redirect = False
        mock_response.raw.version = 11

        mock_requests.request.return_value = mock_response

        assert make_request('http://example.com', 'GET', [], [], 0) == {
            'status': 200,
            'errors': None,
            'data': {
                'response': [
                    {
                        'http_version': 'HTTP/1.1',
                        'status_code': 200,
                        'headers': {}
                    }
                ],
                'request': [
                    {
                        'method': 'GET',
                        'url': 'http://example.com'
                    }
                ]
            }
        }
