import os
import asyncio
import aiohttp
from fastapi import FastAPI
from dotenv import load_dotenv 
from checkenv import check_env, EnvNotSet
from python_files import ll_http_requests ,ll_deta_base, ll_telegram, ll_lms_crawl

load_dotenv()

async def main():
    async with aiohttp.ClientSession() as session:
        # Login to save Cookies
        cookies_dict = await ll_http_requests.login_async(session=session,
                                        lms_username=os.getenv('LMS_USERNAME'),
                                        lms_password=os.getenv('LMS_PASSWORD'),
                                        login_url='http://lms.ui.ac.ir/login')
        
        
        css_selectors = {
            'user': '.feed_item_username',
            'message': '.feed_item_bodytext',
            'attachment': '.feed_item_attachments',
            'date': '.timestamp',
        }

        GROUP_URLs = await ll_lms_crawl.group_urls_async(session=session,
                            lms_homepage_url='http://lms.ui.ac.ir/members/home',)

        ll_deta_base.initialize_db('lms')

        # Fetch Each Group new activity
        tasks = [asyncio.create_task(ll_lms_crawl.process_activity(
            session=session, group_url=group_url, css_selectors=css_selectors
        )) for group_url in GROUP_URLs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        anything_new = any(results)
        if not anything_new:
            return None

        all_in_one_results = [activity for group_activity in results for activity in group_activity]

        empty = await ll_deta_base.database_is_empty()
        await ll_deta_base.put_many(all_in_one_results)
        if empty:
            await ll_deta_base.put({'state': 'initialized'})
            message = f'LMS-Log v0.4.0a\nتعداد {len(all_in_one_results)} پیام در سامانه ال‌ام‌اس پردازش شد و ربات آماده است.'  # noqa: E501
            info_senders = [ll_telegram.send_single_msg(session=session, message=message),
                            ll_telegram.send_async_log(msg=f'new user added, or maybe reset their data\n{os.getenv("LMS_USERNAME")}')  # noqa: E501
            ]
            await asyncio.gather(*info_senders)
        else:
            await ll_telegram.send_msg_list(
                session=session,
                new_activity=all_in_one_results
            )

app = FastAPI()
@app.post('/__space/v0/actions')
@app.get('/')
def root():
    try:
        check_env()
        asyncio.run(main())
    except EnvNotSet as e:
        return f'{e}'
    except Exception as e:
        asyncio.run(ll_telegram.send_async_log(msg=f'{str(e)}\nBy: {os.getenv("LMS_USERNAME")}', msg_type='ERROR'))
        return f"Error!\n{e}"
    return "DONE!"
