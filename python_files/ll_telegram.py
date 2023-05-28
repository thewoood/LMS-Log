import requests
import os

def send_msg(formatted_difference: dict) -> None:
    # repair difference
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
            with open('log.json', 'a+', encoding='utf-8') as file:
                file.write(str(response.text))
            print(f'----Telegram , CHAT-ID: {CHAT_ID}: {response.status_code}----')

def chat_ids() -> list:
    CHAT_IDs_env = os.getenv('CHAT_IDs')
    return CHAT_IDs_env.split(',')

def token() -> str:
    return os.getenv('TEL_BOT_TOKEN')

def unempty_difference(formatted_difference: dict) -> list:
    difference = []
    for key in formatted_difference.keys():
        if formatted_difference[key]['public_activity'] != []:
            for activity in formatted_difference[key]['public_activity']:
                difference.append(activity)
    
    return difference  
def prettify_msg(difference):
    user = f"\N{BUST IN SILHOUETTE} {difference['user']}:"
    message = f"\N{pencil} {difference['message']}"
    attachment = f"\N{link symbol} [{difference['attachment']}]({difference['attachment_link']})"
    date = f"\N{clock face two oclock}{difference['date']}"
    # return f"{user}\n{message}\n{attachment}\n{date}"
    return f"{user}\n\n{message}\n\n<a href='{difference['attachment_link']}'>{difference['attachment']}</a>\n\n{date}"

"""
{user} <br /> {msg} <br /> <a href={url}>{atachment_name}</a> <br /> {date}
"""
