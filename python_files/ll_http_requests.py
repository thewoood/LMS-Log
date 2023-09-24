
import aiohttp

async def aio_get_request(session: aiohttp.ClientSession, url: str,
                          text:bool=False):
    async with session.get(url) as response:
        if text:
            try:
                return await response.text()
            except aiohttp.ClientPayloadError as _:
                return ''
        return response

async def aio_post_request(session: aiohttp.ClientSession, url: str, 
                           payload: dict, text:bool=False) -> aiohttp.ClientResponse:
    async with session.post(url, data = payload) as response:
        if text:
            return await response.text()
        return response


async def login_async(
        session: aiohttp.ClientSession, 
        lms_username: str,
        lms_password: str, 
        login_url: str
) -> dict:
    payload = {
        'username': lms_username,
        'password': lms_password
    }
    async with session.post(
        url=login_url, data=payload, headers={'referrer': login_url}
    ) as _:
        pass        