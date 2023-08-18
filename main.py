import os
import time
import json
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

        old_data = ll_json.download_dict('data.json')
        # Log
        with open('old_data.json',mode='w+' ,encoding='utf-8') as file:
            file.write(json.dumps(old_data, ensure_ascii=False))
        
        # Fetch Each Group new  
        tasks = [asyncio.create_task(ll_lms_crawl.fetch_compare_public_activity(
            session=session, old_data=old_data, group_url=group_url,
            css_selectors=css_selectors
        )) for group_url in GROUP_URLs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        with open('results.json', 'w+', encoding='utf-8') as file:
            file.write(str(results))

        formatted_difference = {}

        for result in results:
            formatted_difference.update(result)
        
        # print(f'formatted difference: {formatted_difference}')
        # await ll_telegram.send_async_log(msg='fuck'+str(results)[:100])
        merged_old_and_difference = ll_lms_crawl.merge_activities_old_and_difference(
            old_data=old_data, difference=formatted_difference)
        # print(f'MERGED SHIT = {merged_old_and_difference}')
        # print(f'formatted difference: {formatted_difference}')

        ll_json.upload_dict(file_name='data.json', content=merged_old_and_difference) 
        old_data = ll_json.download_dict('data.json')
        with open('newdata.json', mode='w+', encoding='utf-8') as file:
            file.write(json.dumps(old_data,ensure_ascii=False))
        await ll_telegram.send_msg(session=session, formatted_difference=formatted_difference)

app = FastAPI()
@app.get('/')
async def root():
    try:
        from tests import test
        await test.test_deta_base_put()
        # await main()
    except Exception as e:
        # with open('log.log', 'w+') as log:
        #     log.write(str(e))
        await ll_telegram.send_async_log(msg=str(e))
        raise e
    return "<h1>Hello</h1>"

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)