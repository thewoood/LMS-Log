import os
from fastapi import FastAPI
from python_files import ll_cookies, ll_json, ll_telegram, ll_lms_crawl
import asyncio

def cookies() -> dict:
    lms_username = os.getenv('LMS_USERNAME')
    lms_password = os.getenv('LMS_PASSWORD')

    cookies_dict = ll_cookies.upload_cookies(lms_username=lms_username, lms_password=lms_password,
                              login_url='http://lms.ui.ac.ir/login', file_name='cookies.pkl')
    # cookies_pickle = ll_cookies.download_cookies(file_name='cookies.pkl')
    return cookies_dict

async def scrape_url(old_data: dict, group_url: str, css_selectors: dict, cookies_dict: dict) -> dict:
    group_name = ll_lms_crawl.group_name_from_url(group_url=group_url)
    ll_telegram.send_log(f'{group_name} 1. start')
    new_data = await ll_lms_crawl.public_activity(group_url=group_url, css_selectors=css_selectors, cookies=cookies_dict)
    old_data_public_activity = old_data.get(group_name, {}).get('public_activity', [])
    difference = ll_lms_crawl.difference_of_activities(new_data=new_data, old_data=old_data_public_activity)
    ll_telegram.send_log(f'{group_name} 4. finished')
    return {group_name:{'public_activity': difference}}
    
async def main():
    cookies_dict = cookies()
    css_selectors = {'user': '.feed_item_username',
                     'message': '.feed_item_bodytext',
                     'attachment': '.feed_item_attachments',
                     'date': '.timestamp',
                     }
    formatted_difference = {}
    
    GROUP_URLS = ll_lms_crawl.group_urls(lms_homepage_url='http://lms.ui.ac.ir/members/home', cookies=cookies_dict)
    old_data = ll_json.download_dict('data2.json')
    
    result = await asyncio.gather(*[scrape_url(old_data=old_data, group_url=group_url, 
                    css_selectors=css_selectors, cookies_dict=cookies_dict) for group_url in GROUP_URLS])
    
    ll_telegram.send_log(str(result))
    # for group_url in GROUP_URLS:
        # diff = scrape_url(old_data=old_data, group_url=group_url, 
        #            css_selectors=css_selectors, cookies_dict=cookies_dict)
        # formatted_difference.update(diff)    
    
    # ll_telegram.send_msg(formatted_difference=formatted_difference)
    # merged_old_and_difference = ll_lms_crawl.merge_activities_old_and_difference(old_data=old_data, 
    #                                                                              difference=formatted_difference)
    # ll_json.upload_dict(file_name='data.json', content=merged_old_and_difference)

from env import Set_Environ
Set_Environ()
app = FastAPI()
@app.get('/')
def root():
    try:
       asyncio.run(main())
    except BaseException as e:
        ll_telegram.send_log(str(e))
    return "<h1>Hello</h1>"