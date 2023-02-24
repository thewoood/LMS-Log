from lxml import html
import requests
from requests import utils
from time import sleep
import pickle
import os
from bs4 import BeautifulSoup



# def isCookieSaved():
#     file_path = 'cookies.pkl'
#     if os.path.isfile(file_path):
#         return True
#     else:
#         return False
    
 
def SaveCookie(username, password,):
    #1: Log in 
    #2: Save Cookies in Cookies.pkl
    
    session_requests=requests.session()
    
    login_url = "http://lms.ui.ac.ir/login"
    result = session_requests.get(login_url) #Loading Login Url

	#Setting Up Login Info
    payload = {
		"username": username,
        "password": password,
	}

	#Logging in 
    result = session_requests.post(
		login_url, 
		data = payload, 
		headers = dict(referer=login_url),
	)
    
 
	# Status Code
    print(result.status_code)
    with open('page.html', 'w', encoding='utf-8') as page:
        page.write(result.text)
 
    
    with open("cookies.pkl", "wb") as f:
        pickle.dump(utils.dict_from_cookiejar(session_requests.cookies), f)
        
    session_requests.close()
    


def Get_Activity(urls, css_selectors): 
    messages = [dict()] 
    session_requests = requests.session()
 
	# Loading the cookies
    with open("cookies.pkl", "rb") as f:
        session_requests.cookies.update(utils.cookiejar_from_dict(pickle.load(f)))
    
    
        
    result = session_requests.get(
            urls[0], 
            headers = dict(referer = urls[0]),
        )
    #Getting the code of the page, Encoding cuz of Persian
    result.apparent_encoding
    soup = BeautifulSoup(result.content, 'lxml')
        

      
    for url in urls:
        result = session_requests.get(
            url, 
            headers = dict(referer = url),
        )
        
        #Getting the code of the page, Encoding cuz of Persian
        result.apparent_encoding
        soup = BeautifulSoup(result.content, 'lxml')
        
        # Users
        users = soup.select(css_selectors[0])
        if users is not None:
            print(f'users length: {len(users)}')
            for user in users:
                msg = {'user': user.text, 'text': '', 'attach': ''}
                messages.append(msg)
        
        # Texts
        texts = soup.select(css_selectors[1])
        if texts is not None:
            print(f'texts length: {len(texts)}')
            for index, text in enumerate(texts):
                messages[index]['text'] = text.text
                
        # Attach
        attachs = soup.select(css_selectors[2])
        if attachs is not None:
            print(f'attachs length: {len(attachs)}')
            for index, attach in enumerate(attachs):
                messages[index]['attach'] = attach.text
        
    print(messages)

def Print_Activity():
    # Save cookies in cookies.pkl
    SaveCookie('4014013109','1991174322')
        
    url = ['http://lms.ui.ac.ir/group/84632']

    css_selectors= ['.feed_item_username',
                    '.feed_item_bodytext',
                    '.feed_item_attachments']
    Get_Activity(urls=url, css_selectors=css_selectors)
 
    
def main():
    Print_Activity()
    
    
if __name__ == '__main__':
    main()
    
'''
TODO
1) Cookie Expiration
2) csv file of all messages so far
3) checking all classes instead of just mabani
4) خب به این نتیجه رسیدیم که چون بعضی پیاما اتچمنت ندارن، سایز لیست اتچشمنت ها با
سایز لیست یوزر ها یکی نمیشه و میترکه. پس چی کار میکنیم؟ هر بار یک بلاک کامل از پیام رو
استخراج میکنیم و بعد توش کنکاش انجام میدیم. سی اس اس سلکتور هر بلاک پیام:
.wall-action-item
میشه با chat gpt فهمید که چطوری به کلاس های توی این بلاک نفوذ کرد
'''