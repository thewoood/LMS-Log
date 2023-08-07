import os
import time
import uvicorn
import asyncio
from aiohttp import ClientSession
import aiohttp
from fastapi import FastAPI
from env import Set_Environ
Set_Environ()
from python_files import ll_cookies, ll_json, ll_telegram, ll_lms_crawl

async def main():
    async with aiohttp.ClientSession() as session:
        cookies_dict = await ll_cookies.login_async(session=session,
                                        lms_username=os.getenv('LMS_USERNAME'),
                                        lms_password=os.getenv('LMS_PASSWORD'),
                                        login_url='http://lms.ui.ac.ir/login')
        
        # await ll_telegram.send_async_log(session=session, msg='main func, cookies: ' + str(cookies_dict))
        css_selectors = {'user': '.feed_item_username',
                     'message': '.feed_item_bodytext',
                     'attachment': '.feed_item_attachments',
                     'date': '.timestamp',
                    }
        GROUP_URLs = await ll_lms_crawl.group_urls_async(session=session,
                            lms_homepage_url='http://lms.ui.ac.ir/members/home',)
        # await ll_telegram.send_async_log(msg='first'+str(GROUP_URLs))
        old_data = ll_json.download_dict('data2.json')
        tasks = [asyncio.create_task(ll_lms_crawl.new_public_activity(
            session=session, old_data=old_data, group_url=group_url,
            css_selectors=css_selectors
        )) for group_url in GROUP_URLs]
        results = await asyncio.gather(*tasks)

        formatted_difference = {}
        for result in results:
            formatted_difference |= result
        # await ll_telegram.send_async_log(msg='fuck'+str(results)[:100])
        merged_old_and_difference = ll_lms_crawl.merge_activities_old_and_difference(
            old_data=old_data, difference=formatted_difference)
        ll_json.upload_dict(file_name='data.json', content=merged_old_and_difference) 
        await ll_telegram.send_msg(session=session, formatted_difference=formatted_difference)

app = FastAPI()
@app.get('/')
async def root():
    try:
        await main()
    except Exception as e:
        # with open('log.log', 'w+') as log:
        #     log.write(str(e))
        await ll_telegram.send_async_log(msg=str(e))
        raise e
    return "<h1>Hello</h1>"

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)