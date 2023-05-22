import requests
from requests import utils
from time import sleep
import pickle
from bs4 import BeautifulSoup
import csv
from github import Github
import io
from io import StringIO
import os
from deta import Deta
from flask import Flask, request
import json
# from env import Set_Environ 
# Set_Environ()
    

def Save_Cookies(lms_username, lms_password, login_url, file_name):
    # 1: Log in
    # 2: Save Cookies in Cookies.pkl
    session_requests = requests.session()

    result = session_requests.get(login_url)  # Loading Login Url

    # Setting Up Login Info
    payload = {
        "username": lms_username,
        "password": lms_password,
    }

    # Logging in
    result = session_requests.post(
        login_url,
        data=payload,
        headers=dict(referer=login_url),
    )

    # Status Code
    print(f'{login_url}: {result.status_code}')

    # Upload cookies to Deta Drive
    cookies = utils.dict_from_cookiejar(session_requests.cookies)
    cookies_pickle = pickle.dumps(cookies)
    drive.put(file_name, cookies_pickle, content_type='application/octet-stream')
    print('----Cookies Uploaded!----')
    
    session_requests.close()


def Load_Cookies(file_name):
    cookies_deta_drive = drive.get(file_name)
    cookies_pickle = pickle.loads(cookies_deta_drive.read())
    cookies_deta_drive.close()
    print(f'----Is "cookies_deta_drive" closed: {cookies_deta_drive.closed}-----')
    return cookies_pickle

def Get_Group_Links(lms_homepage_url: str, cookies: pickle) -> list:
    session_requests = requests.session()
    session_requests.cookies.update(utils.cookiejar_from_dict(cookies))
    
    result = session_requests.get(
        url=lms_homepage_url,
        headers=dict(referer=lms_homepage_url),
    )
    
    result.apparent_encoding
    soup = BeautifulSoup(result.text, 'html.parser')
    
    #Extract all profiles
    profile_groups = soup.find('ul', id='profile_groups')
    group_a_tags = profile_groups.find_all('a')
    group_links = [group_a_tag['href'] for group_a_tag in group_a_tags]

    return group_links
    
def Get_LMS_Messages(url: str, css_selectors:dict, cookies: pickle):
    session_requests = requests.session()

    # Loading the cookies
    session_requests.cookies.update(utils.cookiejar_from_dict(cookies))

    result = session_requests.get(
        url,
        headers=dict(referer=url),
    )

    # Getting the code of the page, Encoding cuz of Persian
    result.apparent_encoding
    soup = BeautifulSoup(result.content, 'html.parser')

    msg_boxes = soup.select('.wall-action-item')

    activities = []
    for msg_box in msg_boxes:
        html = msg_box.prettify()
        sub_soup = BeautifulSoup(html, 'html.parser')
        
        user = sub_soup.select_one(css_selectors['user'])
        
        message = sub_soup.select_one(css_selectors['message'])
        message = '' if message is None else message.text
        
        attachment = sub_soup.select_one(css_selectors['attachment'])
        attachment_text = '' if attachment is None else attachment.text
        attachment_link = f'https://lms.ui.ac.ir/{attachment.find("a")["href"]}' if attachment != None else ''

        # find the "timestamp" span element within the "feed_item_date" div
        feed_item_date = sub_soup.find('div', class_='feed_item_date')
        timestamp_span = feed_item_date.find('span', class_='timestamp')
        # extract the time as a string
        time_str = timestamp_span['title']
        
        msg = {
            'user': user.text.strip().replace('\n\n', ''),
            'message': message.strip().replace('\n\n', ''),
            'attachment': attachment_text.strip().replace('\n\n', ''),
            'attachment_link': attachment_link,
            'date': time_str.strip().replace('\n\n', '')
               }

        activities.append(msg)
    
    print(f'{url.split("/")[-1]}: {len(activities)} MESSAGES - LMS')
    return activities

def Whats_New(url: str, css_selectors: dict,):
    # filename = f"{url.split('/')[-1]}.csv"
    old_data = Load_Json('data.json')
    new_data = Get_LMS_Messages(url, css_selectors,)
    
    # lesson_name = url.split('/')[-1]
    # old_data = old_data.get(lesson_name, {}).get('public_activity', [])
    difference = [activity for activity in new_data if activity not in old_data]
    with open('log.txt', 'w+', encoding='utf-8') as file:
        file.write(str(difference))
    
    # Commented to check functionality of Get_LMS_Messages
    '''previous_data = Load_CSV(filename, repo_main_url, token)
    # check if there is non csv file relateed to the lesson in github, or it's empty
    if previous_data is None:
        differences = new_data
    else:
        differences = [data for data in new_data if data not in previous_data]

    Send_Diff_In_Github(differences, csv_headers, username, token,
                        repository_name, 'messageholder.csv', repo_main_url)
    repo_name = repo_main_url.split('/')[-3]
    Save_CSV(new_data, filename, csv_headers, username,
             token, repo_name, len(differences))'''


def Get_Message_Holder(repo_main_url, token):
    message_holder = Load_CSV('messageholder.csv', repo_main_url, token)
    return message_holder


def Send_Diff_In_Github(differences, csv_headers, username, token, repository_name, file_name, repo_main_url):
    previous_message_holder = Get_Message_Holder(repo_main_url, token)
    len_new_data = len(differences)
    
    if len_new_data != 0:
        # File details
        csv_data = io.StringIO(newline='\n')
        csv_writer = csv.DictWriter(csv_data, fieldnames=csv_headers)
        csv_writer.writeheader()
        csv_writer.writerows(previous_message_holder)
        csv_writer.writerows(differences)

        # Read CSV file content
        file_content = csv_data.getvalue()

        # Authenticate with GitHub
        g = Github(username, token)

        # Get the repository
        repo = g.get_user().get_repo(repository_name)

        # Check if the file exists
        try:
            file = repo.get_contents(file_name)
            # Update the existing file
            repo.update_file(file.path, 'Updated!', file_content, file.sha)
            print(f'{len_new_data} added to github messageholder.csv!')
        except:
            # Create a new file
            repo.create_file(file_name, 'Created!', file_content)
            print(
                f'File "{file_name}" created and uploaded successfully. {len_new_data} added to github messageholder.csv!')
    else:
        print('0 new messages. No update to messageholder.csv Github!')


def prettify_msg(msg, csv_headers):
    return f"{msg[csv_headers[0]]}:\n{msg[csv_headers[1]]}\n{msg[csv_headers[2]]}\n{msg[csv_headers[3]]}"


def Save_CSV(data, filename, csv_hearders, username, token, repository_name, len_new_data):
    Upload_CSV_Github(username, token, filename, data,
                      csv_hearders, repository_name, len_new_data)


def Set_Ending(listofdict):
    unix_data = [{k: v.replace('\r\n', '\n') for k, v in d.items()} for d in listofdict]
    return unix_data
      

def Load_Json(file_name: str) -> json.load:
    json_drive = drive.get(file_name)
    data_json = json.load(json_drive)
    return data_json
      
def Load_CSV(filename, repo_main_url, token, ):
    # GitHub repository URL
    url = repo_main_url+filename

    # HTTP headers
    headers = {'Authorization': f'token {token}'}

    # Make the HTTP request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Convert the response content to a string buffer
        content = response.content.decode('utf-8')
        buffer = StringIO(content, newline='\n')

        # Read the CSV file from the string buffer
        reader = csv.DictReader(buffer)
        data = list(reader)

        # Print the data
        print(f'{len(data)} rows loaded from {filename} successfully!')
        data = Set_Ending(data)
        return data
    else:
        print('Failed to read the CSV file.')


def Upload_CSV_Github(username, token, file_name, new_data, csv_headers, repository_name, len_new_data):
    if len_new_data != 0:
        # File details
        csv_data = io.StringIO(newline='\n')
        csv_writer = csv.DictWriter(csv_data, fieldnames=csv_headers)
        csv_writer.writeheader()
        csv_writer.writerows(new_data)

        # Read CSV file content
        file_content = csv_data.getvalue()

        # Authenticate with GitHub
        g = Github(username, token)

        # Get the repository
        repo = g.get_user().get_repo(repository_name)

        # Check if the file exists
        try:
            file = repo.get_contents(file_name)
            # Update the existing file
            repo.update_file(file.path, 'Updated!', file_content, file.sha)
            print(f'{len_new_data} new messages added to {file_name}')
        except:
            # Create a new file
            repo.create_file(file_name, 'Created!', file_content)
            print(
                f'File "{file_name}" created and uploaded successfully. {len_new_data} new messages added to {file_name}')
    else:
        print(f'No messages added to {file_name}!')


def main():
    # Save cookies in cookies.pkl
    # Run this if you're local
    from env import Set_Environ
    Set_Environ()

    lms_username = os.getenv('LMS_USERNAME')
    lms_password = os.getenv('LMS_PASSWORD')

    Save_Cookies(lms_username, lms_password, "http://lms.ui.ac.ir/login", 'cookies.pkl')
    cookies_pickle = Load_Cookies('cookies.pkl')
    
    groups_links = Get_Group_Links('http://lms.ui.ac.ir/members/home', cookies=cookies_pickle)
    full_group_links = ['http://lms.ui.ac.ir/' + group_link for group_link in groups_links]
    
    css_selectors = {'user': '.feed_item_username',
                     'message': '.feed_item_bodytext',
                     'attachment': '.feed_item_attachments',
                     'date': '.timestamp',
                     }
    
    Get_LMS_Messages(url= full_group_links[3], css_selectors=css_selectors,cookies=cookies_pickle)
    # Commented to see if deta drive stores cookies correctly 
    '''csv_headers = ['User', 'Text', 'Attach', 'Date']

    for url in urls:
        Whats_New(url, username, token, css_selectors,
                  csv_headers, repo_main_url, repo_name)'''



deta = Deta()
drive = deta.Drive('My_Storage')

app = Flask(__name__)

@app.route('/')
def start():
    main()
    return "<h1>Hello!</h1>"