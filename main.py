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
   
   
def Make_Raw_Data_Json(deta_file_name: str, group_names: list) -> None:
    raw_data = {} 
    for group_name in group_names:
         raw_data += {
            group_name.split('/')[-1]: 
                {
                    'public_activity': [],
                    'private_message': []
                }
                    }
    data_json = json.dumps(raw_data) 
    drive.put(name=deta_file_name, data=data_json, content_type='application/json')
    print('---- Raw "data.json" uploaded to deta drive ----')
    
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

def GET_Difference_of_Activity_LMS(group_name, old_data: dict, new_data: dict):
    # old_data = Load_Json(deta_file_name)
    # new_data = Get_LMS_Messages(url, css_selectors, cookies)
    # lesson_name = url.split('/')[-1]
    # old_data = old_data.get(group_name, {}).get('public_activity', [])
    difference = [activity for activity in new_data if str(activity) not in old_data]
    
    # for i in range(len(new_data)):
    #     for (letter1, letter2) in zip(str(new_data[i]), str(old_data[i-1])):
    #         with open('log.txt', 'a+', encoding='utf-8') as file:
    #             file.write(str(letter1 == letter2))
    with open('log.txt', 'w+', encoding='utf-8') as file:
        file.write(str(old_data[2])+'\n')
        file.write(str(new_data[3]))
        
    '''SEND Difference to Telegram'''
    '''Overwrite the newdata'''
  
        
    # old_data[group_name]['public_activity'] = new_data
    return difference
    # Upload_Json(old_data, deta_file_name)
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

def Load_Json(file_name: str) -> dict:
    json_drive = drive.get(file_name)
    if json_drive:
        data_json = json.load(json_drive)
        data_json = json.loads(data_json)

        return dict(data_json)
    return dict()

def Upload_Json(new_data:dict, file_name: str):
    file_data = json.dumps(new_data)
    drive.put(file_name, file_data, content_type="application/json")
      
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
    
    groups_links_endings = Get_Group_Links('http://lms.ui.ac.ir/members/home', cookies=cookies_pickle)
    full_group_links = ['http://lms.ui.ac.ir/' + group_link for group_link in groups_links_endings]
    
    css_selectors = {'user': '.feed_item_username',
                     'message': '.feed_item_bodytext',
                     'attachment': '.feed_item_attachments',
                     'date': '.timestamp',
                     }
    old_data = Load_Json('data.json')
    new_data = Get_LMS_Messages(full_group_links[2], css_selectors, cookies_pickle)
    # if not old_data:
    #     Make_Raw_Data_Json('data.json', full_group_links)
    
    group_public_activity = old_data.get(full_group_links[2].split('/')[-1], {}).get('public_activity', [])
 
    difference = GET_Difference_of_Activity_LMS(group_name=full_group_links[2].split('/')[-1], old_data=group_public_activity, new_data=new_data)
    json_new_data = {full_group_links[2].split('/')[-1]:{'public_activity': new_data}}
    old_data |= json_new_data
            
    json_old_data = json.dumps(old_data)
    test_json = {'84632': {'public_activity': [
    {'user': 'علیرضا نصراصفهانی', 'message': 'با سلام. نمرات میانترم به پیوست می باشد.', 'attachment': '001.jpg', 'attachment_link': 'https://lms.ui.ac.ir/public/group/9a/9a/0f/f7c0f_7e23.jpg', 'date': '۲۴ ارديبهشت ۰۲, ۰۵:۴۱ عصر'
    },
    {'user': 'علیرضا نصراصفهانی', 'message': '', 'attachment': 'mabani6.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/fd/1f/0f/f01ed_a250.pdf', 'date': '۳ اسفند ۰۱, ۰۲:۰۵ عصر'
    },
    {'user': 'علیرضا نصراصفهانی', 'message': '', 'attachment': 'mabani5.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/fc/1f/0f/f01ec_d427.pdf', 'date': '۳ اسفند ۰۱, ۰۲:۰۵ عصر'
    },
    {'user': 'علیرضا نصراصفهانی', 'message': '', 'attachment': 'mabani4.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/fb/1f/0f/f01eb_39e8.pdf', 'date': '۳ اسفند ۰۱, ۰۲:۰۵ عصر'
    },
    {'user': 'علیرضا نصراصفهانی', 'message': '', 'attachment': 'mabani3.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/29/13/0f/ef525_b07a.pdf', 'date': '۲۳ بهمن ۰۱, ۰۴:۳۶ عصر'
    },
    {'user': 'علیرضا نصراصفهانی', 'message': '', 'attachment': 'mabani2.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/28/13/0f/ef524_76e2.pdf', 'date': '۲۳ بهمن ۰۱, ۰۴:۳۵ عصر'
    },
    {'user': 'زين الدين - عرفان', 'message': 'لینک گروه مبانی ریاضی t.me/+XqE8mzeqp-YzMzc0', 'attachment': '', 'attachment_link': '', 'date': '۲۱ بهمن ۰۱, ۰۷:۲۳ عصر'
    },
    {'user': 'علیرضا نصراصفهانی', 'message': '', 'attachment': 'بنام خداوند جان و خرد.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/12/0d/0f/eef14_3fa2.pdf', 'date': '۱۶ بهمن ۰۱, ۱۱:۵۲ صبح'
    },
    {'user': 'علیرضا نصراصفهانی', 'message': '', 'attachment': 'mabani1.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/11/0d/0f/eef13_638b.pdf', 'date': '۱۶ بهمن ۰۱, ۱۱:۵۲ صبح'
    },
    {'user': 'علیرضا نصراصفهانی', 'message': 'با سلام خدمت دانشجویان گرامی. سرفصل, مراجع و فایل جلسات درس به پیوست می باشد.', 'attachment': 'mabanikol.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/10/0d/0f/eef12_3f2c.pdf', 'date': '۱۶ بهمن ۰۱, ۱۱:۵۲ صبح'
    }
]
}, '84643': {'public_activity': [
    {'user': 'فاطمه دوست محمدي', 'message': 'درود بر دانشجویان گرامی\n     \n      تمرین های مربوط به فصل 15\n      \n       *شماره تمرین های عملی : 14 - 18 - 28 - 29\n       \n        *شماره تمرین های بخش 7 : 11 - 19\n        \n         لطفا این تمرینات را برای جلسه...\n         \n          بیشتر\n         \n     درود بر دانشجویان گرامی\n     \n      تمرین های مربوط به فصل 15\n      \n       *شماره تمرین های عملی : 14 - 18 - 28 - 29\n       \n        *شماره تمرین های بخش 7 : 11 - 19\n        \n         لطفا این تمرینات را برای جلسه شنبه مورخ 30 اردیبهشت حل نمایید.\n         \n          چند تمرین دیگر از بخش 15 و یک سری تمرین نیز از بخش 16 تعیین میشود که تا چند روز آینده داخل سامانه میگذارم تا برای جلسه های بعدی حل نمایید.', 'attachment': '', 'attachment_link': '', 'date': '۲۲ ارديبهشت ۰۲, ۱۰:۴۴ صبح'
    },
    {'user': 'فاطمه دوست محمدي', 'message': '', 'attachment': 'طرح درس ریاضی 2.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/df/68/0f/f4a86_37f2.pdf', 'date': '۲۶ فروردين ۰۲, ۰۶:۲۹ عصر'
    },
    {'user': 'فاطمه دوست محمدي', 'message': '', 'attachment': 'seri7.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/dc/68/0f/f4a83_1a13.pdf', 'date': '۲۶ فروردين ۰۲, ۰۶:۲۶ عصر'
    },
    {'user': 'فاطمه دوست محمدي', 'message': '', 'attachment': 'seri6.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/db/68/0f/f4a82_3368.pdf', 'date': '۲۶ فروردين ۰۲, ۰۶:۲۶ عصر'
    },
    {'user': 'فاطمه دوست محمدي', 'message': '', 'attachment': 'seri5.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/da/68/0f/f4a81_1a33.pdf', 'date': '۲۶ فروردين ۰۲, ۰۶:۲۵ عصر'
    },
    {'user': 'فاطمه دوست محمدي', 'message': '', 'attachment': 'seri4.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/d9/68/0f/f4a80_6efb.pdf', 'date': '۲۶ فروردين ۰۲, ۰۶:۲۵ عصر'
    },
    {'user': 'فاطمه دوست محمدي', 'message': '', 'attachment': 'seri3.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/d8/68/0f/f4a7f_e09d.pdf', 'date': '۲۶ فروردين ۰۲, ۰۶:۲۵ عصر'
    },
    {'user': 'فاطمه دوست محمدي', 'message': '', 'attachment': 'seri2.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/d7/68/0f/f4a7e_c1a9.pdf', 'date': '۲۶ فروردين ۰۲, ۰۶:۲۵ عصر'
    },
    {'user': 'فاطمه دوست محمدي', 'message': '', 'attachment': 'seri1.pdf', 'attachment_link': 'https://lms.ui.ac.ir/public/group/d6/68/0f/f4a7d_bd74.pdf', 'date': '۲۶ فروردين ۰۲, ۰۶:۲۵ عصر'
    }
]
}
}
    test_json = json.dumps(test_json)
    drive.put('data.json', data=test_json,content_type='application/json')

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