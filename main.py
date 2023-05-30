import os
from fastapi import FastAPI
from python_files import ll_cookies, ll_json, ll_lms, ll_telegram
# from env import Set_Environ
# Set_Environ()

def main():
    # Save cookies in cookies.pkl
    # Run this if you're local

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

    formatted_difference = {}
    for group_link in group_links:
        ll_telegram.send_log('1. start')

        new_data = ll_lms.get_lms_activities(group_link, css_selectors,cookies_pickle)
        ll_telegram.send_log('2. new data')

        old_data_public_activity = old_data.get(group_link.split('/')[-1], {}).get('public_activity', [])
        ll_telegram.send_log('3. old data')


        difference = ll_lms.difference_of_activities(new_data=new_data, old_data=old_data_public_activity)
        formatted_difference.update({group_link.split('/')[-1]:{'public_activity': difference}})
        ll_telegram.send_log('4. formatted')

        ll_telegram.send_log('5. finish')
    ll_telegram.send_msg(formatted_difference=formatted_difference)
    merged_old_and_difference = ll_lms.merge_activities_old_and_difference(old_data=old_data,
                                                                           difference=formatted_difference)


    # Upload new data
    ll_json.upload_dict(file_name='data.json', content=merged_old_and_difference)

app = FastAPI()

@app.get('/')
def root():
    logged = main()
    ll_telegram.send_log(str(logged))
    return "<h1>Hello</h1>"