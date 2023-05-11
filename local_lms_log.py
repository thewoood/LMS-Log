import os
from env import Set_Environ
import pickle
import requests 
from requests import utils
from bs4 import BeautifulSoup

def main():
    # Save cookies in cookies.pkl
    # Run this if you're local
    Set_Environ()
    
    username = os.getenv('GITHUB_USERNAME')
    token = os.getenv('GITHUB_TOKEN')
    repo_name = os.getenv('GITHUB_REPO_NAME')
    lms_username = os.getenv('LMS_USERNAME')
    lms_password = os.getenv('LMS_PASSWORD')
    SaveCookie(lms_username, lms_password, "http://lms.ui.ac.ir/login")
    urls = ['http://lms.ui.ac.ir/group/84643',
            'http://lms.ui.ac.ir/group/83713',
            'http://lms.ui.ac.ir/group/84632',
            'http://lms.ui.ac.ir/group/84738',
            'http://lms.ui.ac.ir/group/84675',]
    csv_headers = ['User', 'Text', 'Attach', 'Date']
    css_selectors = ['.feed_item_username',
                     '.feed_item_bodytext',
                     '.feed_item_attachments',
                     '.timestamp',
                     ]
    repo_main_url = f'https://raw.githubusercontent.com/{username}/{repo_name}/main/'
    for url in urls:
        Whats_New(url, username, token, css_selectors,
                  csv_headers,)



def SaveCookie(username, password, login_url):
    # 1: Log in
    # 2: Save Cookies in Cookies.pkl

    session_requests = requests.session()

    result = session_requests.get(login_url)  # Loading Login Url

    # Setting Up Login Info
    payload = {
        "username": username,
        "password": password,
    }

    # Logging in
    result = session_requests.post(
        login_url,
        data=payload,
        headers=dict(referer=login_url),
    )

    # Status Code
    print(result.status_code)

    cookies = utils.dict_from_cookiejar(session_requests.cookies)
    Save_Cookies_To_Local(cookies)

    session_requests.close()



def Save_Cookies_To_Local(cookies):
    # Read CSV file content
    file_content = pickle.dumps(cookies)

    with open('./my_drive/cookies.pkl', 'wb') as cookies:
        cookies.write(file_content)


def Whats_New(url, token, css_selectors, csv_headers, repo_main_url):
    filename = f"{url.split('/')[-1]}.csv"
    new_data = Get_Messages(
        url, css_selectors, csv_headers,)
    return new_data


def Get_Messages(url, css_selectors, csv_headers):
    messages = []
    session_requests = requests.session()

    # Loading the cookies
    c = Load_Cookies_From_Local()
    session_requests.cookies.update(utils.cookiejar_from_dict(c))

    result = session_requests.post(
        url,
        headers=dict(referer=url),
        data={'javascript': 'void(0);'}
    )

    # Getting the code of the page, Encoding cuz of Persian
    result.apparent_encoding
    
    print('Writing data on webpage...')
    with open('page.html', 'wb',) as page:
        page.write(result.content)
        
    soup = BeautifulSoup(result.content, 'html.parser')


    msg_boxes = soup.select('.wall-action-item')

    for msg_box in msg_boxes:
        html = msg_box.prettify()
        sub_soup = BeautifulSoup(html, 'html.parser')
        
        user = sub_soup.select_one(css_selectors[0])
        text = sub_soup.select_one(css_selectors[1])
        attach = sub_soup.select_one(css_selectors[2])
        feed_item_date = sub_soup.find('div', class_='feed_item_date')
        # find the "timestamp" span element within the "feed_item_date" div
        timestamp_span = feed_item_date.find('span', class_='timestamp')
        # extract the time as a string
        time_str = timestamp_span['title']
        attach = '' if attach is None else attach.text

        msg = {
            csv_headers[0]: user.text.strip().replace('\n\n', ''),
            csv_headers[1]: text.text.strip().replace('\n\n', ''),
            csv_headers[2]: attach.strip().replace('\n\n', ''),
            csv_headers[3]: time_str.strip().replace('\n\n', '')
               }

        messages.append(msg)

    print(f'{len(messages)} rows read from lms!')
    return messages

# Gets a url and sends it to social media
def Load_Cookies_From_Local():
    
    with open('./my_drive/cookies.pkl', 'rb') as cookies:
        cookies = pickle.load(cookies)
        return cookies

main()
