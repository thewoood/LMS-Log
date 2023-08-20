import os
import time
import json
import uvicorn
import asyncio
from aiohttp import ClientSession
import aiohttp
from fastapi import FastAPI
# from env import Set_Environ
# Set_Environ()
from python_files import ll_cookies, ll_deta_base, ll_telegram, ll_lms_crawl

async def main():
    async with aiohttp.ClientSession() as session:
        # Login to save Cookies
        cookies_dict = await ll_cookies.login_async(session=session,
                                        lms_username=os.getenv('LMS_USERNAME'),
                                        lms_password=os.getenv('LMS_PASSWORD'),
                                        login_url='http://lms.ui.ac.ir/login')
        
        
        css_selectors = {'user': '.feed_item_username',
                     'message': '.feed_item_bodytext',
                     'attachment': '.feed_item_attachments',
                     'date': '.timestamp',
                    }

        GROUP_URLs = await ll_lms_crawl.group_urls_async(session=session,
                            lms_homepage_url='http://lms.ui.ac.ir/members/home',)

        ll_deta_base.initialize_db()

        # Fetch Each Group new activity
        tasks = [asyncio.create_task(ll_lms_crawl.process_activity(
            session=session, group_url=group_url, css_selectors=css_selectors
        )) for group_url in GROUP_URLs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        allinone_results = [activity for group_activity in results for activity in group_activity]

        await ll_deta_base.put_many(allinone_results)
            
        await ll_telegram.send_msg(session=session, new_activity=allinone_results)

app = FastAPI()
@app.get('/')
async def root():
    try:
        await main()
    except Exception as e:
        with open('log.log', 'w+') as log:
            log.write(str(e))
        await ll_telegram.send_async_log(msg=str(e))
        raise e
    return "<h1>Hello</h1>"

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)