
import aiohttp

async def aio_get_request(session: aiohttp.ClientSession, url: str,
                          text:bool=False):
    async with session.get(url) as response:
        if text:
            return await response.text()
        return response

async def aio_post_request(session: aiohttp.ClientSession, url: str, 
                           payload: dict, text:bool=False) -> aiohttp.ClientResponse:
    async with session.post(url, data = payload) as response:
        if text:
            return await response.text()
        return response
