import os
import asyncio
import aiohttp
import requests
from python_files.ll_http_requests import aio_post_request

def send_log(msg: str) -> list[requests.Response]:
    CHAT_IDs = chat_ids()
    TOKEN = token()
    telegram_url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    print('sending shit')
    response = requests.post(url=telegram_url, json={'text': msg,
                                 'chat_id': CHAT_IDs[0]})

    return response

async def send_async_log(session: aiohttp.ClientSession, msg: str) -> list[requests.Response]:
    CHAT_IDs = chat_ids()
    TOKEN = token()
    telegram_url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

    senders = [aio_post_request(session = session, url=telegram_url,
                                payload={'text': msg, 'chat_id': chat_id})
                                for chat_id in CHAT_IDs]
    
    return await asyncio.gather(*senders, return_exceptions=True)
    # for finished_task in asyncio.as_completed(senders):
    #     await finished_task

def send_msg(formatted_difference: dict) -> None:
    # repair difference
    send_log(f'telegram send_msg')

    difference = unempty_difference(formatted_difference=formatted_difference)

    # Prepare
    CHAT_IDs = chat_ids()
    TOKEN = token()
    session = requests.Session()
    # for difference in differences:
    for CHAT_ID in CHAT_IDs:
        for activity in difference:
            msg = prettify_msg(activity)
            telegram_url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
            response = session.post(telegram_url, json={
                'text': msg,                
                'chat_id': CHAT_ID,
                'parse_mode': 'HTML'
                })
            print(f'----Telegram , CHAT-ID: {CHAT_ID}: {response.status_code}----')

def chat_ids() -> list:
    CHAT_IDs_env = os.getenv('CHAT_IDs')
    return CHAT_IDs_env.split(',')

def token() -> str:
    return os.getenv('TEL_BOT_TOKEN')

def unempty_difference(formatted_difference: dict) -> list:
    '''returns a list of activities that are unmepty
    '''
    difference = []
    for key in formatted_difference.keys():
        if formatted_difference[key]['public_activity'] != []:
            for activity in formatted_difference[key]['public_activity']:
                difference.append(activity)
    
    return difference  

def prettify_msg(difference):
    user = f'\N{BUST IN SILHOUETTE} {difference["user"]}:'
    message = f'\N{pencil} {difference["message"]}'
    attachment_url = difference['attachment_url']
    attachment_text = difference['attachment_text']
    date = f'\N{clock face two oclock} {difference["date"]}'
    return f'{user}\n\n{message}\n\n<a href="{attachment_url}">{attachment_text}</a>\n\n{date}'

