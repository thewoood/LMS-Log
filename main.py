import os

# from flask import Flask
from typing import Any, Awaitable
from fastapi import FastAPI
import asyncio, aiohttp
from python_files import ll_cookies, ll_json, ll_lms, ll_telegram
from env import Set_Environ

Set_Environ()


async def old_data_public_activity(old_data: dict, group_name: str) -> dict:
    old_data_public_activity = old_data.get(group_name).get("public_activity", [])
    ll_telegram.send_log(f"{group_name}: 2. new data")

    return old_data_public_activity


async def difference_and_format(
    new_data: list, old_data: list, group_name: str
) -> dict:
    difference = ll_lms.difference_of_activities(new_data=new_data, old_data=old_data)
    formatted_difference = {group_name: {"public_activity": difference}}
    ll_telegram.send_log(f"{group_name}: 4. formatted / finished")

    return formatted_difference


async def run_parallel(*functions: Awaitable[Any]) -> list:
    return await asyncio.gather(*functions)


async def run_sequence(*functions: Awaitable[Any]) -> list:
    return_values = []
    for function in functions:
        return_values += await function

    return return_values


async def scrape_url(group_link, old_data, css_selectors, cookies_pickle):
    group_name = group_link.split("/")[-1]
    ll_telegram.send_log("1. start")

    # new_data = await ll_lms.get_lms_activities(group_link, css_selectors, cookies_pickle)

    # _old_data_public_activity = await old_data_public_activity(old_data=old_data, group_name=group_name)
    # ll_telegram.send_log('3. old data')

    # formatted_difference = await difference_and_format(new_data=new_data,
    #                                                    old_data=_old_data_public_activity,
    #                                                    group_name=group_name)

    new_data, _old_data_public_activity = run_parallel(
        ll_lms.get_lms_activities(
            group_url=group_link, css_selectors=css_selectors, cookies=cookies_pickle
        ),
        old_data_public_activity(old_data=old_data, group_name=group_name),
    )

    formatted_difference = await difference_and_format(
        new_data=new_data, old_data=_old_data_public_activity, group_name=group_name
    )
    return formatted_difference


async def main():
    # Save cookies in cookies.pkl
    # Run this if you're local

    lms_username = os.getenv("LMS_USERNAME")
    lms_password = os.getenv("LMS_PASSWORD")

    old_data = ll_json.download_dict("data2.json")
    css_selectors = {
        "user": ".feed_item_username",
        "message": ".feed_item_bodytext",
        "attachment": ".feed_item_attachments",
        "date": ".timestamp",
    }

    ll_cookies.upload_cookies(
        lms_username=lms_username,
        lms_password=lms_password,
        login_url="http://lms.ui.ac.ir/login",
        file_name="cookies.pkl",
    )

    cookies_pickle = ll_cookies.download_cookies(file_name="cookies.pkl")

    group_links = await ll_lms.get_group_links(
        "http://lms.ui.ac.ir/members/home", cookies=cookies_pickle
    )

    formatted_differences = {}

    async with aiohttp.ClientSession() as session:
        tasks = []
        for group_link in group_links:
            task = scrape_url(
                group_link=group_link,
                css_selectors=css_selectors,
                old_data=old_data,
                cookies_pickle=cookies_pickle,
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

    for result in results:
        formatted_differences.update(result)

    # with open('log.json', 'w', encoding='utf-8') as file:
    #     file.write(str(formatted_differences))

    ll_telegram.send_msg(formatted_difference=formatted_differences)
    merged_old_and_difference = ll_lms.merge_activities_old_and_difference(
        old_data=old_data, difference=formatted_differences
    )
    # Upload new data
    ll_json.upload_dict(file_name="data.json", content=merged_old_and_difference)


app = FastAPI()


@app.get("/")
def root():
    asyncio.run(main())
    return "<h1>Hello</h1>"
