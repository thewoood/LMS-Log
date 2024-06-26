from bs4 import BeautifulSoup
from aiohttp import ClientSession

from python_files.ll_lms_Activity_Box import Msg_Box
from .ll_http_requests import aio_get_request
from .ll_deta_base import list_of_dicts_exists_in_base

async def process_activity(
        session: ClientSession,
        group_url: str, 
        css_selectors: dict
) -> list[dict]:

    fetched_activity = await fetch_activity(
        session=session,
        group_url=group_url,
        css_selectors=css_selectors
    )
    new_activity = await list_of_dicts_exists_in_base(fetched_activity)
    return new_activity

async def fetch_activity(session: ClientSession, group_url: str,
                                css_selectors: dict) -> list[dict]:

    page_html_content = await aio_get_request(session=session, url=group_url, text=True)
    soup = BeautifulSoup(page_html_content, 'html.parser')
    msg_boxes = soup.select('.wall-action-item')
    activities = []
    group_name = group_name_from_url(group_url=group_url)
    for msg_box in msg_boxes:
        html = msg_box.prettify()
        sub_soup = BeautifulSoup(html, 'html.parser')
        class_msg_box = Msg_Box(sub_soup=sub_soup, css_selectors=css_selectors,group=group_name)  # noqa: E501
        activities.append(class_msg_box.setup_msg())
    
    print(f'{group_name}: {len(activities)} MESSAGES - LMS')
    return activities

async def group_urls_async(session: ClientSession, lms_homepage_url: str) -> list:
    home_page_text = await aio_get_request(session=session, 
                                      text=True, url=lms_homepage_url)
    # home_page_text = await home_page.text(encoding='utf-8')
    soup = BeautifulSoup(home_page_text, 'html.parser')
    group_a_tags = soup.find('ul', id='profile_groups').find_all('a')
    group_names = [group_a_tag['href'] for group_a_tag in group_a_tags]
    return ['http://lms.ui.ac.ir' + group_name for group_name in group_names]


def group_name_from_url(group_url: str) -> str:
    '''Extract group name using group URL'''
    return group_url.split("/")[-1]

def difference_of_activities(new_data: list, old_data: list) -> dict:
    difference = [new_row for new_row in new_data if new_row not in old_data]
    return difference

def merge_activities_old_and_difference(old_data: dict, difference: dict) -> dict:
    old_data.update(difference)
    return old_data