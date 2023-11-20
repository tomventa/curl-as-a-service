from fastapi import HTTPException
from urllib.parse import urlparse
import requests
import ipaddress
import socket
from app.models.shared import JSONException

def url_info(url: str) -> dict[str, str]:
    """Decompose an URL into its components.

    Args:
        url (str): The URL to decompose.

    Returns:
        dict[str, str]: The decomposed URL.
                        URL: The original URL.
                        protocol: The URL protocol (http, https, ftp, ...).
                        domain: The URL domain (www.google.com, www.amazon.com, ...).
                        path: The URL path (/, /search, /search/test/, '').
    """
    try:
        parsed_url = urlparse(url)
    except Exception as e:
        raise JSONException(id='INVALID_URL', detail='The URL you provided is invalid')

    return {
        "url": url,
        "protocol": parsed_url.scheme,
        "domain": parsed_url.netloc,
        "path": parsed_url.path
    }

def resolve_ip(input: str) -> str | None:
    # If the input is an IP, return it
    try:
        ip_object = ipaddress.ip_address(input)
        return input
    except ValueError:
        # Resolve the domain
        try:
            return socket.gethostbyname(input)
        except socket.gaierror:
            raise JSONException(id='INVALID_DOMAIN_RECORD', detail='The domain url is pointing to an invalid IP address')
        


def detect_ssrf(url: str) -> bool:
    """Detect if the given URL has an host that points to a private IP address.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL has an host that points to a private IP address, False otherwise.
    """
    # Parse the URL and get the domain
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
    except Exception as e:
        return False
    # Check if the domain is an IP
    ip = resolve_ip(domain)
    if ip is None:
        return False
    # Check if IP is private
    ip_object = ipaddress.ip_address(ip)
    return ip_object.is_private


def make_request(url: str, method: str, request_list: list = [], responses: list = [], redirect_count: int = 0) -> dict:
    """Make a HTTP request to the given URL.

    Args:
        url (str): URL to make the request to.
        method (str): HTTP method to use. Must be one of: post, get, put, delete, info.
        request_list (list, optional): Previous history of performed request. Defaults to [].
        responses (list, optional): Previous history of received responses. Defaults to [].
        redirect_count (int, optional): Redirect counter. Prevents infinite redirection. Defaults to 0.

    Returns:
        dict: Dict in standard "HTTPResponse" format. See app/models/api.py for more details.
    """
    
    # Detect SSRF
    if detect_ssrf(url):
        raise JSONException(id='SSRF_DETECTED', detail='The URL you provided is a private IP address. This is not allowed')

    # Append the current request to the list of requests
    request_list.append({
        'method': method,
        'url': url
    })

    try:
        response = requests.request(method, url, allow_redirects=False)
    except Exception as e:
        return JSONException(id='REQUEST_EXCEPTION', detail=f'Generic request exception: {e}')

    # If the response is a redirect and the redirect counter is greater than 5, return an error
    if response.is_redirect and redirect_count >= 10:
        raise JSONException(id='TOO_MANY_REDIRECTS', detail='Too many redirects while following the url you provided')

    # Filter the headers to keep only the ones we want to show
    headers_to_keep = ['Content-Type', 'Content-Length', 'Date', 'Server', 'Location']
    filtered_headers = {key: value for key, value in response.headers.items() if key in headers_to_keep}

    # Append the current response to the list of responses
    responses.append({
        'http_version': f'HTTP/{response.raw.version / 10}',
        'status_code': response.status_code,
        'headers': filtered_headers
    })

    # If the response is a redirect (3xx), call the function again with the redirected URL
    if not response.is_redirect:
        return {
            'status': 200,
            'errors': None,
            'data': {
                'response': responses,
                'request': request_list
            }
        }
        
    # If the response is a redirect, call the function again with the redirected URL
    redirect_count += 1
    redirected_url = response.headers['Location']
    return make_request(redirected_url, method, request_list, responses, redirect_count)
