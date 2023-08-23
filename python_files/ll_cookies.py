import pickle
import requests
import aiohttp
from python_files import ll_telegram

def get_cookies(lms_username: str, lms_password: str, login_url: str) -> dict:
    with requests.Session() as session:
        payload = {
        "username": lms_username,
        "password": lms_password,
        }

        response = session.post(
            url=login_url,
            data=payload,
            headers=dict(referer=login_url)
        )
        print(f'----{login_url}: {response.status_code}----')
        cookies_dict = requests.utils.dict_from_cookiejar(session.cookies)
    
    return cookies_dict

async def login_async(session: aiohttp.ClientSession, 
                            lms_username: str, lms_password: str, 
                            login_url: str) -> dict:
    payload = {
        'username': lms_username,
        'password': lms_password
    }
    async with session.post(url=login_url, data=payload,
                            headers={'referer': login_url}) as response:
        pass

def upload_cookies(cookies_dict: dict, file_name: str) -> None:
    cookies_pickle = pickle.dumps(cookies_dict)
    upload_result = ll_deta_drive.upload_file(file_name=file_name, content=cookies_pickle)
    print(f'----Cookies Uploaded!----: {upload_result}\n')

def download_cookies(file_name: str) -> pickle:
    cookies_deta_drive = ll_deta_drive.download_file(file_name=file_name)
    cookies_pickle = pickle.loads(cookies_deta_drive.read())
    print(f'----Is "cookies_deta_drive" closed: {cookies_deta_drive.closed}-----')
    return cookies_pickle
