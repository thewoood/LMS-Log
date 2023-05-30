
import pickle
# import requests
import aiohttp, asyncio
from bs4 import BeautifulSoup
import gzip

# def get_page_html(url: str, cookies: pickle) -> list:
#     session_requests = requests.session()
#     session_requests.cookies.update(requests.utils.cookiejar_from_dict(cookies))
    
#     result = session_requests.get(
#         url=url,
#         headers=dict(referer=url),
#     )
    
#     result.apparent_encoding
#     return result
async def get_page_html(session, url: str, cookies: pickle) -> str:
    async with session.get(url, headers={'referer': url,}, cookies=cookies) as response:
        if response.headers.get("Content-Encoding") == "gzip":
            # Manually decompress the response content if it is gzip-encoded
            content = await response.read()
            try:
                decompressed_content = gzip.decompress(content).decode("utf-8")
            except gzip.BadGzipFile:
                # The response content is not actually gzip-encoded, fallback to decoding as text
                decompressed_content = content.decode("utf-8")
            return decompressed_content
        else:
            # Response content is not gzip-encoded, decode as text
            content = await response.text()
            return content
async def get_group_links(lms_homepage_url: str, cookies: pickle) -> list:
    # home_page = get_page_html(url=lms_homepage_url, cookies=cookies)
    async with aiohttp.ClientSession() as session:
        home_page = await get_page_html(session=session, url=lms_homepage_url, cookies=cookies)
    
    #Extract names of groups
    soup = BeautifulSoup(home_page, 'html.parser')
    group_a_tags = soup.find('ul', id='profile_groups').find_all('a')
    group_names = [group_a_tag['href'] for group_a_tag in group_a_tags]

    return ['http://lms.ui.ac.ir' + group_name for group_name in group_names]


async def get_lms_activities(group_url: str, css_selectors: dict, cookies: pickle) -> list[dict]:

    # Load page
    # page_html = get_page_html(url=group_url, cookies=cookies)
    async with aiohttp.ClientSession() as session:
        page_html = await get_page_html(session=session, url=group_url, cookies=cookies)
    # Exteact Cards 
    soup = BeautifulSoup(page_html, 'html.parser')
    msg_boxes = soup.select('.wall-action-item')

    activities = []
    for msg_box in msg_boxes:
        html = msg_box.prettify()
        sub_soup = BeautifulSoup(html, 'html.parser')
        
        # Finding elements of Message
        user = sub_soup.select_one(css_selectors['user'])
        
        message = sub_soup.select_one(css_selectors['message'])
        message = '' if message is None else message.text
        
        attachment = sub_soup.select_one(css_selectors['attachment'])
        attachment_text = '' if attachment is None else attachment.text
        attachment_link = f'https://lms.ui.ac.ir{attachment.find("a")["href"]}' if attachment != None else ''

        # find the "timestamp" span element within the "feed_item_date" div
        feed_item_date = sub_soup.find('div', class_='feed_item_date')
        timestamp_span = feed_item_date.find('span', class_='timestamp')
        # extract the time as a string
        time_str = timestamp_span['title']
        
        # Prepare Message
        msg = {
            'user': user.text.strip().replace('\n\n', ''),
            'message': message.strip().replace('\n\n', ''),
            'attachment': attachment_text.strip().replace('\n\n', ''),
            'attachment_link': attachment_link,
            'date': time_str.strip().replace('\n\n', '')
               }

        activities.append(msg)
    
    group_name = group_url.split("/")[-1]
    print(f'{group_name}: {len(activities)} MESSAGES - LMS')
    return activities


def difference_of_activities(new_data: list, old_data: list) -> dict:
    difference = [new_row for new_row in new_data if new_row not in old_data]
    return difference

def merge_activities_old_and_difference(old_data: dict, difference: dict) -> dict:
    return old_data | difference