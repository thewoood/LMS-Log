import os
from flask import Flask
from python_files import ll_cookies, ll_json, ll_lms


def main():
    # Save cookies in cookies.pkl
    # Run this if you're local
    from env import Set_Environ
    Set_Environ()

    lms_username = os.getenv('LMS_USERNAME')
    lms_password = os.getenv('LMS_PASSWORD')

    ll_cookies.upload_cookies(lms_username=lms_username, lms_password=lms_password,
                              login_url='http://lms.ui.ac.ir/login', file_name='cookies.pkl')
    
    cookies_pickle = ll_cookies.download_cookies(file_name='cookies.pkl')
    
    group_links = ll_lms.get_group_links('http://lms.ui.ac.ir/members/home', cookies=cookies_pickle)
    
    css_selectors = {'user': '.feed_item_username',
                     'message': '.feed_item_bodytext',
                     'attachment': '.feed_item_attachments',
                     'date': '.timestamp',
                     }
    
    old_data = ll_json.download_dict('data2.json')
    
    group_link = group_links[0]
    
    new_data = ll_lms.get_lms_activities(group_link, css_selectors,cookies_pickle)
    old_data_public_activity = old_data.get(group_link.split('/')[-1], {}).get('public_activity', [])


    difference = ll_lms.difference_of_activities(new_data=new_data, old_data=old_data_public_activity)
    formatted_difference = {group_link.split('/')[-1]:{'public_activity': difference}}
    merged_old_and_difference = ll_lms.merge_activities_old_and_difference(old_data=old_data, difference=formatted_difference)
    with open('log.json', 'w+', encoding='utf-8') as file:
        file.write(str(merged_old_and_difference))

    # Upload new data
    ll_json.upload_dict(file_name='data.json', content=merged_old_and_difference)

app = Flask(__name__)

@app.route('/')
def start():
    main()
    return "<h1>Hello!</h1>"