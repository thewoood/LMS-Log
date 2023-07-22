
import requests
import asyncio
import aiohttp

async def aio_get_request(session: aiohttp.ClientResponse, url: str):
    async with session.get(url) as response:
        return response

async def aio_post_request(session: aiohttp.ClientSession, url: str, 
                           payload: dict) -> aiohttp.ClientResponse:
    async with session.post(url, data = payload) as response:
        return response
        
def get_request(url: str, cookies: dict=None) -> requests.Response:
    with requests.Session() as session:
        if cookies != None:
            session.cookies.update(requests.utils.cookiejar_from_dict(cookies))
        result = session.get(url=url, headers=dict(referer=url))
        result.apparent_encoding
    return result

async def get_async_request(url: str, cookies: dict = None) -> requests.Response:
    return await asyncio.to_thread(get_request, url)

def post_request(url: str, _json: dict) -> requests.Response:
    with requests.Session() as session:
        response = session.post(url=url, json=_json)
    return response

async def post_async_request(url: str, _json: dict = None) -> requests.Response:
    return await asyncio.to_thread(post_request, **{'url': url, '_json': _json})
