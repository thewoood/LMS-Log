import requests
from requests import utils
from time import sleep
import pickle
from bs4 import BeautifulSoup
import csv
from github import Github
import io
from io import StringIO
import socket
import urllib3
 
def SaveCookie(username, password, login_url, gituser, gittoken, repository_name, cookiename):
    #1: Log in 
    #2: Save Cookies in Cookies.pkl
    
    session_requests=requests.session()
    
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
    
    cookies = utils.dict_from_cookiejar(session_requests.cookies)
    Save_Cookies_To_Github(gituser, gittoken, repository_name, cookiename, cookies)
    
    # with open("cookies.pkl", "wb") as f:
    #     pickle.dump(utils.dict_from_cookiejar(session_requests.cookies), f)
        
    session_requests.close()
    
def Save_Cookies_To_Github(username, token, repository_name, file_name, cookies):
    # Read CSV file content
    file_content = pickle.dumps(cookies)

    # Authenticate with GitHub
    g = Github(username, token)

    # Get the repository
    repo = g.get_user().get_repo(repository_name)

    # Check if the file exists
    try:
        file = repo.get_contents(file_name)
        # Update the existing file
        repo.update_file(file.path, 'Updated!', file_content, file.sha)
        print('cookies updated!')
    except :
        # Create a new file
        repo.create_file(file_name, 'Created!', file_content)
        print('cookies created.')

def Load_Cookies_From_Github(repo_main_url, filename, token):
    # GitHub repository URL
    url = repo_main_url+filename

    # HTTP headers
    headers = {'Authorization': f'token {token}'}

    # Make the HTTP request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Convert the response content to a string buffer
        content = io.BytesIO(response.content)
        # buffer = StringIO(content)

        # Loading the cookies
        
        cookies = pickle.load(content)
        return cookies

    else:
        print('Failed to read the Cookies file.')

def Get_Messages(url, css_selectors, csv_headers, token, repo_main_url): 
    messages = [] 
    session_requests = requests.session()
 
	# Loading the cookies
    c = Load_Cookies_From_Github(repo_main_url, 'cookies.pkl', token)
    session_requests.cookies.update(utils.cookiejar_from_dict(c))

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
        feed_item_date = sub_soup.find('div', class_='feed_item_date')
        # find the "timestamp" span element within the "feed_item_date" div
        timestamp_span = feed_item_date.find('span', class_='timestamp')
        # extract the time as a string
        time_str = timestamp_span['title']
        if attach is None:
            attach = ''
        else:
            attach = attach.text

        msg = {csv_headers[0]: user.text.strip().replace('\n\n', ''),
            csv_headers[1]: text.text.strip().replace('\n\n', ''),
            csv_headers[2]: attach.strip().replace('\n\n', ''),
            csv_headers[3]: time_str.strip().replace('\n\n', '')
            }
        
        messages.append(msg)
    
    print(f'{len(messages)} rows read from lms!')
    return messages      

# Gets a url and sends it to social media 
def Whats_New(url, username, token, css_selectors, csv_headers, repo_main_url, repository_name):
    filename = f"{url.split('/')[-1]}.csv"
    new_data = Get_Messages(url, css_selectors, csv_headers, token, repo_main_url)
    previous_data = Load_CSV(filename, repo_main_url, token)
    differences = [data for data in new_data if data not in previous_data]
    repo_name = repo_main_url.split('/')[-3]
    Send_Diff_In_Github(differences, csv_headers, username, token, repository_name, 'messageholder.csv', repo_main_url)
    Save_CSV(new_data, filename, csv_headers, username, token, repo_name, len(differences))
  
def Get_Message_Holder(repo_main_url, token):
    message_holder = Load_CSV('messageholder.csv', repo_main_url, token)
    return message_holder
    
def Send_Diff_In_Github(differences, csv_headers, username, token, repository_name, file_name, repo_main_url):
    previous_message_holder = Get_Message_Holder(repo_main_url, token)
    len_new_data = len(differences)
    if len_new_data != 0:
        # File details
        csv_data = io.StringIO()
        csv_writer = csv.DictWriter(csv_data, fieldnames=csv_headers)
        csv_writer.writeheader()
        csv_writer.writerows(previous_message_holder)
        csv_writer.writerows(differences)

        # Read CSV file content
        file_content = csv_data.getvalue()

        # Authenticate with GitHub
        g = Github(username, token)

        # Get the repository
        repo = g.get_user().get_repo(repository_name)

        # Check if the file exists
        try:
            file = repo.get_contents(file_name)
            # Update the existing file
            repo.update_file(file.path, 'Updated!', file_content, file.sha)
            print(f'{len_new_data} added to github message holder!')
        except :
            # Create a new file
            repo.create_file(file_name, 'Created!', file_content)
            print(f'File "{file_name}" created and uploaded successfully. {len_new_data} added to github message holder!')
    else:
        print('0 new messages. No update to Github!')

def prettify_msg(msg, csv_headers):
    return f"{msg[csv_headers[0]]}:\n{msg[csv_headers[1]]}\n{msg[csv_headers[2]]}\n{msg[csv_headers[3]]}"

def Save_CSV(data, filename, csv_hearders, username, token, repository_name, len_new_data):
    Upload_CSV_Github(username,token, filename, data, csv_hearders, repository_name, len_new_data)
    
def Load_CSV(filename, repo_main_url, token, ):
    # GitHub repository URL
    url = repo_main_url+filename

    # HTTP headers
    headers = {'Authorization': f'token {token}'}

    # Make the HTTP request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Convert the response content to a string buffer
        content = response.content.decode('utf-8')
        buffer = StringIO(content)

        # Read the CSV file from the string buffer
        reader = csv.DictReader(buffer)
        data = list(reader)

        # Print the data
        print(f'{len(data)} rows loaded from {filename} successfully!')
        return data
    else:
        print('Failed to read the CSV file.')

def Upload_CSV_Github(username, token, file_name, new_data, csv_headers, repository_name, len_new_data):
    if len_new_data !=0:
        # File details
        csv_data = io.StringIO()
        csv_writer = csv.DictWriter(csv_data, fieldnames=csv_headers)
        csv_writer.writeheader()
        csv_writer.writerows(new_data)

        # Read CSV file content
        file_content = csv_data.getvalue()

        # Authenticate with GitHub
        g = Github(username, token)

        # Get the repository
        repo = g.get_user().get_repo(repository_name)

        # Check if the file exists
        try:
            file = repo.get_contents(file_name)
            # Update the existing file
            repo.update_file(file.path, 'Updated!', file_content, file.sha)
            print(f'{len_new_data} new messages added!')
        except :
            # Create a new file
            repo.create_file(file_name, 'Created!', file_content)
            print(f'File "{file_name}" created and uploaded successfully. {len_new_data} new messages added!')
    else:
        print('0 new messages!')


def main():
    # Save cookies in cookies.pkl
    username = 'thewoood'
    token = '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'
    SaveCookie('4014013109','1991174322', "http://lms.ui.ac.ir/login", username, token, 'lms-cloud', 'cookies.pkl')
        
    urls = ['http://lms.ui.ac.ir/group/84632',
           'http://lms.ui.ac.ir/group/84738',
           'http://lms.ui.ac.ir/group/84675',
           'http://lms.ui.ac.ir/group/84643']
    csv_headers = ['User', 'Text', 'Attach', 'Date']
    css_selectors= ['.feed_item_username',
                '.feed_item_bodytext',
                '.feed_item_attachments',
                '.timestamp',
                ]
    # telegram_chat_id = '-1001694255282'
    # cloud_flare_url = 'https://lms-log.davwvod.workers.dev/'
    repo_main_url = 'https://raw.githubusercontent.com/thewoood/lms-cloud/main/'
    for url in urls:
        Whats_New(url, username, token, css_selectors, csv_headers, repo_main_url, 'lms-cloud')

    
if __name__ == '__main__':
    while True:
        main()
        print('Wating for 900 seconds')
        sleep(1800)
    
'''
i want to send a post requests to 'https://lms-log.davwvod.workers.dev' using this DNS-over-HTTPS: https://free.shecan.ir/dns-query
TODO
1) DONE
Cookie Expiration
2) DONE
    save info in csv, load from csv, compare list with csv 
    EACH CLASS HAS A DIFFERENT CSV FILE
3) DONE
    checking all classes instead of just mabani
4) DONE
خب به این نتیجه رسیدیم که چون بعضی پیاما اتچمنت ندارن، سایز لیست اتچشمنت ها با
سایز لیست یوزر ها یکی نمیشه و میترکه. پس چی کار میکنیم؟ هر بار یک بلاک کامل از پیام رو
استخراج میکنیم و بعد توش کنکاش انجام میدیم. سی اس اس سلکتور هر بلاک پیام:
.wall-action-item
میشه با chat gpt فهمید که چطوری به کلاس های توی این بلاک نفوذ کرد
5) DONE
    save files in a private github repo
6) is it possible to send message in telegram using Liara? 
    Answer: FUCK NO!
    
    
7) DONE
    Save date and time of message: .timestamp
8) Send the link of attachment
9) DONE!
    Load data from github
10) Load cookies from github
11) Save cookies to github
12) Restructure the code
    use black.py to pretiffy it
13) DONE
    since we read csv from github, the returned value is not string and can't be updated
15) DONE
    a function to get previous and new, and return what's different 
'''
