import os
import asyncio
from aiohttp import ClientSession
import requests
import datetime
from python_files.ll_http_requests import aio_post_request

def chat_ids() -> list:
    CHAT_IDs_env = os.getenv('CHAT_IDs')
    return CHAT_IDs_env.split(',')

def token() -> str:
    return os.getenv('TEL_BOT_TOKEN')

async def send_async_log(session: ClientSession = None,
                         msg: str = '') -> list[ClientSession]:
    CHAT_IDs = chat_ids()
    TOKEN = token()
    telegram_url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    msg = f'[{datetime.datetime.now().isoformat()}]\n\n' + msg
    if session is not None:
        senders = [asyncio.create_task(aio_post_request(session = session, url=telegram_url,
                                payload={'text': msg, 'chat_id': chat_id}))
                                for chat_id in CHAT_IDs]
    else:
        async with ClientSession() as _session:
            senders = [asyncio.create_task(aio_post_request(session = _session, url=telegram_url,
                                payload={'text': msg, 'chat_id': chat_id}))
                                for chat_id in CHAT_IDs]
    
            return await asyncio.gather(*senders)
    return await asyncio.gather(*senders)


async def send_sigle_msg(session: ClientSession, message: str) -> None:
    
    CHAT_IDs = chat_ids()
    TOKEN = token()
    session = requests.Session()
    # for difference in differences:
    telegram_url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    senders = []
    for CHAT_ID in CHAT_IDs:
        task = asyncio.create_task(
                aio_post_request(session=session, url=telegram_url,
                                payload={
                                        'text': message,                
                                        'chat_id': CHAT_ID,
                                        'parse_mode': 'HTML'
                                }))
        senders.insert(0, task)
    await asyncio.gather(*senders, return_exceptions=True)
async def send_msg_list(session: ClientSession, new_activity: list) -> None:

    difference = new_activity
    # Prepare
    CHAT_IDs = chat_ids()
    TOKEN = token()
    session = requests.Session()
    # for difference in differences:
    telegram_url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    senders = []
    for activity in difference:
        for CHAT_ID in CHAT_IDs:
            msg = prettify_msg(activity)
            senders.append(asyncio.create_task(
                aio_post_request(session=session, url=telegram_url,
                                 payload={
                                        'text': msg,                
                                        'chat_id': CHAT_ID,
                                        'parse_mode': 'HTML'
                                }
                )
            )
            )
            # print(f'----Telegram , CHAT-ID: {CHAT_ID}: {response.status_code}----')
    if len(senders) > 15:
        msg = f' با توجه به بالا بودن تعداد پیام های جدید و گروه های فعال(مجموعا {len(senders)} پیام)، ممکن است deta space صرفا بخشی از پیام ها را ارسال کند.'
        for CHAT_ID in CHAT_IDs:
            task = asyncio.create_task(
                    aio_post_request(session=session, url=telegram_url,
                                    payload={
                                            'text': msg,                
                                            'chat_id': CHAT_ID,
                                            'parse_mode': 'HTML'
                                    }))
            senders.insert(0, task)
    await asyncio.gather(*senders, return_exceptions=True)

def prettify_msg(difference):
    user = f'\N{BUST IN SILHOUETTE} {difference["user"]}:' if difference['user'] != 'LmsLogNone' else ''
    message = f'\N{pencil} {difference["message"]}' if difference['message'] != 'LmsLogNone' else ''
    attachment_url = difference['attachment_url'] if difference['attachment_url'] != 'LmsLogNone' else ''
    attachment_text = difference['attachment_text'] if difference['attachment_text'] != 'LmsLogNone' else ''
    date = f'\N{clock face two oclock} {difference["date"]}' if difference['date'] != 'LmsLogNone' else ''
    return f'{user}\n\n{message}\n\n<a href="{attachment_url}">{attachment_text}</a>\n\n{date}'

