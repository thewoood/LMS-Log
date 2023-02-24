from lxml import html
import requests
from requests import utils
from time import sleep
import pickle
import os
from bs4 import BeautifulSoup
 
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
    messages = [] 
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
        soup = BeautifulSoup(result.content, 'html.parser') 
       
        msg_boxes = soup.select('.wall-action-item')
        
        for msg_box in msg_boxes:
            html = msg_box.prettify()
            sub_soup = BeautifulSoup(html, 'html.parser')
            user = sub_soup.select_one(css_selectors[0])
            text = sub_soup.select_one(css_selectors[1])
            attach = sub_soup.select_one(css_selectors[2]) 
            if attach is None:
                attach = ''
            else:
                attach = attach.text

            msg = {'user': user.text.strip(),
                'text': text.text.strip(),
                'attach': attach.strip(),
                }
            
            messages.append(msg)
        for msg in messages:
            print(msg)
   
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
1) DONE
Cookie Expiration
2) save info in csv, load from csv, compare list with csv 
    EACH CLASS HAS A DIFFERENT CSV FILE
3) checking all classes instead of just mabani
4) DONE
خب به این نتیجه رسیدیم که چون بعضی پیاما اتچمنت ندارن، سایز لیست اتچشمنت ها با
سایز لیست یوزر ها یکی نمیشه و میترکه. پس چی کار میکنیم؟ هر بار یک بلاک کامل از پیام رو
استخراج میکنیم و بعد توش کنکاش انجام میدیم. سی اس اس سلکتور هر بلاک پیام:
.wall-action-item
میشه با chat gpt فهمید که چطوری به کلاس های توی این بلاک نفوذ کرد
'''
