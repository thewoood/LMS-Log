
import pickle
import requests

def get_page_html(url: str, cookies: pickle) -> list:
    session_requests = requests.session()
    session_requests.cookies.update(requests.utils.cookiejar_from_dict(cookies))
    
    result = session_requests.get(
        url=url,
        headers=dict(referer=url),
    )
    
    result.apparent_encoding
    return result