import pickle
import requests
from python_files import ll_deta_drive

def upload_cookies(lms_username: str, lms_password: str, login_url: str, file_name: str) -> dict:
    # 1: Log in
    # 2: Save Cookies in Cookies.pkl
    session_requests = requests.session()
    result = session_requests.get(login_url)  # Loading Login Url
    # Setting Up Login Info
    payload = {
        "username": lms_username,
        "password": lms_password,
    }
    # Logging in
    result = session_requests.post(
        login_url,
        data=payload,
        headers=dict(referer=login_url),
    )
    # Status Code
    print(f'----{login_url}: {result.status_code}----')
    # Upload cookies to Deta Drive
    raw_cookies = requests.utils.dict_from_cookiejar(session_requests.cookies)
    cookies_pickle = pickle.dumps(raw_cookies)
    #content_type is defualt
    upload_result = ll_deta_drive.upload_file(file_name=file_name, content=cookies_pickle)
    print(f'----Cookies Uploaded!----\n{upload_result}\n')
    session_requests.close()
    return raw_cookies


def download_cookies(file_name: str) -> dict:
    cookies_deta_drive = ll_deta_drive.download_file(file_name=file_name)
    cookies_pickle = pickle.loads(cookies_deta_drive.read())
    print(f'----Is "cookies_deta_drive" closed: {cookies_deta_drive.closed}-----')
    return cookies_pickle
