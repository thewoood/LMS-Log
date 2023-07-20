from python_files.ll_lms_Msg_Box import Msg_Box
from python_files.ll_http_requests import get_request
from bs4 import BeautifulSoup

def group_urls(lms_homepage_url: str, cookies: dict) -> list:
    '''Extract Name of lms groups'''
    home_page = get_request(url=lms_homepage_url, cookies=cookies)
    soup = BeautifulSoup(home_page.text, 'html.parser')
    group_a_tags = soup.find('ul', id='profile_groups').find_all('a')
    group_names = [group_a_tag['href'] for group_a_tag in group_a_tags]
    return ['http://lms.ui.ac.ir' + group_name for group_name in group_names]


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