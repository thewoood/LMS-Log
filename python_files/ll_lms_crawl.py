from python_files.ll_lms_Msg_Box import Msg_Box
# from python_files.ll_http_requests import get_request
from .ll_http_requests import aio_get_request
from bs4 import BeautifulSoup
from aiohttp import ClientSession

def group_urls(lms_homepage_url: str, cookies: dict) -> list:
    '''Extract Name of lms groups'''
    home_page = get_request(url=lms_homepage_url, cookies=cookies)
    soup = BeautifulSoup(home_page.text, 'html.parser')
    group_a_tags = soup.find('ul', id='profile_groups').find_all('a')
    group_names = [group_a_tag['href'] for group_a_tag in group_a_tags]
    return ['http://lms.ui.ac.ir' + group_name for group_name in group_names]

async def new_public_activity(session: ClientSession, old_data: dict,
                              group_url: str, css_selectors: dict) -> dict:
    group_name = group_name_from_url(group_url=group_url)
    new_data = await public_activity_async(session=session,
                    group_url=group_url, css_selectors=css_selectors)
    old_data_public_activity = old_data.get(group_name, {}).get('public_activity', [])
    difference = difference_of_activities(new_data=new_data, 
                                                       old_data=old_data_public_activity)
    return {group_name:{'public_activity': difference}}

async def group_urls_async(session: ClientSession, lms_homepage_url: str) -> list:
    home_page_text = await aio_get_request(session=session, 
                                      text=True, url=lms_homepage_url)
    # home_page_text = await home_page.text(encoding='utf-8')
    soup = BeautifulSoup(home_page_text, 'html.parser')
    group_a_tags = soup.find('ul', id='profile_groups').find_all('a')
    group_names = [group_a_tag['href'] for group_a_tag in group_a_tags]
    return ['http://lms.ui.ac.ir' + group_name for group_name in group_names]

async def public_activity_async(session: ClientSession, group_url: str,
                                css_selectors: dict) -> list[dict]:
    page_html_content = await aio_get_request(session=session, url=group_url, text=True)
    print(type(page_html_content))
    soup = BeautifulSoup(page_html_content, 'html.parser')
    msg_boxes = soup.select('.wall-action-item')
    activities = []
    for msg_box in msg_boxes:
        html = msg_box.prettify()
        sub_soup = BeautifulSoup(html, 'html.parser')
        class_msg_box = Msg_Box(sub_soup=sub_soup, css_selectors=css_selectors)
        activities.append(class_msg_box.setup_msg())
    
    group_name = group_name_from_url(group_url=group_url)
    print(f'{group_name}: {len(activities)} MESSAGES - LMS')
    return activities

def public_activity(group_url: str, css_selectors: dict, cookies: dict) -> list[dict]:
    '''Extract public messages'''
    page_html = get_request(url=group_url, cookies=cookies)
    soup = BeautifulSoup(page_html.content, 'html.parser')
    msg_boxes = soup.select('.wall-action-item')
    activities = []
    for msg_box in msg_boxes:
        html = msg_box.prettify()
        sub_soup = BeautifulSoup(html, 'html.parser')
        class_msg_box = Msg_Box(sub_soup=sub_soup, css_selectors=css_selectors)
        activities.append(class_msg_box.setup_msg())
    
    group_name = group_name_from_url(group_url=group_url)
    print(f'{group_name}: {len(activities)} MESSAGES - LMS')
    return activities

def group_name_from_url(group_url: str) -> str:
    '''Extract group name using group URL'''
    return group_url.split("/")[-1]

def difference_of_activities(new_data: list, old_data: list) -> dict:
    difference = [new_row for new_row in new_data if new_row not in old_data]
    return difference

def merge_activities_old_and_difference(old_data: dict, difference: dict) -> dict:
    return old_data | difference