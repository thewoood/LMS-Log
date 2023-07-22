
import aiohttp

async def aio_get_request(session: aiohttp.ClientResponse, url: str):
    async with session.get(url) as response:
        return response

async def aio_post_request(session: aiohttp.ClientSession, url: str, 
                           payload: dict) -> aiohttp.ClientResponse:
    async with session.post(url, data = payload) as response:
        return response
