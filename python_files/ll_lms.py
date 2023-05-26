
import pickle
import requests
from bs4 import BeautifulSoup

def get_page_html(url: str, cookies: pickle) -> list:
    session_requests = requests.session()
    session_requests.cookies.update(requests.utils.cookiejar_from_dict(cookies))
    
    result = session_requests.get(
        url=url,
        headers=dict(referer=url),
    )
    
    result.apparent_encoding
    return result

def get_group_links(lms_homepage_url: str, cookies: pickle) -> list:
    home_page = get_page_html(url=lms_homepage_url, cookies=cookies)
    
    #Extract names of groups
    soup = BeautifulSoup(home_page.text, 'html.parser')
    group_a_tags = soup.find('ul', id='profile_groups').find_all('a')
    group_names = [group_a_tag['href'] for group_a_tag in group_a_tags]

    return ['http://lms.ui.ac.ir' + group_name for group_name in group_names]


def get_lms_activities(group_url: str, css_selectors: dict, cookies: pickle) -> list[dict]:

    # Load page
    page_html = get_page_html(url=group_url, cookies=cookies)
    
    # Exteact Cards
    soup = BeautifulSoup(page_html.content, 'html.parser')
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


def difference_of_activities(new_data: list, old_data: list):
    difference = {new_row for new_row in new_data if new_row not in old_data}
    return difference