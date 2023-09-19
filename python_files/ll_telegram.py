import os
import asyncio
from aiohttp import ClientSession
import datetime
from python_files.ll_http_requests import aio_post_request
from python_files.ll_lms_Activity_Box import EMPTY_PLACE_HOLDER

PERSONAL_TOKEN = '6208525679:AAG-oqk3GDmXkRtOk6S-iuhNseQTwNGlVWQ'
def chat_ids() -> list:
    CHAT_IDs_env = os.getenv('CHAT_IDs')
    return CHAT_IDs_env.split(',')

def token() -> str:
    if TOKEN := os.getenv('BOT_TOKEN'):
        return TOKEN
    return PERSONAL_TOKEN

async def send_async_log(session: ClientSession = None,
                         msg: str = '', msg_type: str = 'INFO') -> list[ClientSession]:
    CHAT_ID = '-1001835853718'
    THREAD_ID = '1158'
    TOKEN = PERSONAL_TOKEN
    telegram_url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    msg = f'[{datetime.datetime.now().isoformat()}]\n\n {msg_type}\n\n' + msg
    if bool(session):
        sender = asyncio.create_task(aio_post_request(session = session, url=telegram_url,
                                payload={'text': msg, 'chat_id': CHAT_ID, 
                                         'message_thread_id': THREAD_ID}))
                                
    else:
        async with ClientSession() as _session:
            sender = asyncio.create_task(aio_post_request(session = _session, url=telegram_url,
                                payload={'text': msg, 'chat_id': CHAT_ID,
                                         'message_thread_id': THREAD_ID}))
    
            return await sender
    return await sender


async def send_single_msg(session: ClientSession, message: str) -> None:
    
    CHAT_IDs = chat_ids()
    TOKEN = token()
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
        senders.append(task)
    await asyncio.gather(*senders, return_exceptions=True)
    
async def send_msg_list(session: ClientSession, new_activity: list) -> None:

    difference = new_activity
    # Prepare
    CHAT_IDs = chat_ids()
    TOKEN = token()
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
    if len(senders) > 9:
        msg = f' با توجه به بالا بودن تعداد پیام های جدید و گروه های فعال(مجموعا {len(senders)} پیام در {len(CHAT_IDs)} گروه)، ممکن است Telegram صرفا بخشی از پیام ها را ارسال کند.'
        alerts = []
        for CHAT_ID in CHAT_IDs:
            task = asyncio.create_task(
                    aio_post_request(session=session, url=telegram_url,
                                    payload={
                                            'text': msg,                
                                            'chat_id': CHAT_ID,
                                            'parse_mode': 'HTML'
                                    }))
            alerts.append(task)
        alert_response = await asyncio.gather(*alerts, return_exceptions=False)
    await asyncio.gather(*senders, return_exceptions=False)

def prettify_msg(difference):
    user = f'\N{BUST IN SILHOUETTE}کاربر: {difference["user"]}\n\n' if difference['user'] != EMPTY_PLACE_HOLDER else ''
    message = f'\N{pencil}پیام: {difference["message"]}\n\n' if difference['message'] != EMPTY_PLACE_HOLDER else ''
    attachment_url = f"{difference['attachment_url']}" if difference['attachment_url'] != EMPTY_PLACE_HOLDER else ''
    attachment_text_prefix = f'\N{magnet}پیوست:' if difference['attachment_text'] != EMPTY_PLACE_HOLDER else ''
    attachment_text = f"{difference['attachment_text']}\n\n" if difference['attachment_text'] != EMPTY_PLACE_HOLDER else ''
    half_space = '‌'
    date = f'\N{clock face two oclock}تاریخ: {difference["date"]}\n{half_space}' if difference['date'] != EMPTY_PLACE_HOLDER else ''
    return f'{user}{message}{attachment_text_prefix} <a href="{attachment_url}">{attachment_text}</a>{date}'

