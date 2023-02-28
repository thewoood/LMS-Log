from lxml import html
import requests
from requests import utils
from time import sleep
import pickle
import os
from bs4 import BeautifulSoup
import csv
from github import Github
import io
 
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
    

def Get_Messages(url): 
    messages = [] 
    session_requests = requests.session()
 
	# Loading the cookies
    with open("cookies.pkl", "rb") as f:
        session_requests.cookies.update(utils.cookiejar_from_dict(pickle.load(f)))
        
    # result = session_requests.get(
    #         url, 
    #         headers = dict(referer = url),
    #     )
    # #Getting the code of the page, Encoding cuz of Persian
    # result.apparent_encoding
    # soup = BeautifulSoup(result.content, 'lxml')
        
    
    result = session_requests.get(
        url, 
        headers = dict(referer = url),
    )
    
    #Getting the code of the page, Encoding cuz of Persian
    result.apparent_encoding
    soup = BeautifulSoup(result.content, 'html.parser') 
    
    msg_boxes = soup.select('.wall-action-item')
    
    css_selectors= ['.feed_item_username',
                '.feed_item_bodytext',
                '.feed_item_attachments']
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

        msg = {'User': user.text.strip().replace('\n\n', ''),
            'Text': text.text.strip().replace('\n\n', ''),
            'Attach': attach.strip().replace('\n\n', ''),
            }
        
        messages.append(msg)
    
    
    return messages      

# Gets a url and sends it to social media 
def Whats_New(url):
    filename = f"{url.split('/')[-1]}.csv"
    new_data = Get_Messages(url)
    token = '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'
    previous_data = Load_CSV(filename=filename, token=token)
    # Send_In_Social_Media(new_data,previous_data)
    # Save_CSV(new_data, filename)
    # Upload to github
    Upload_Github('thewoood', token,filename, new_data)

    
def Send_In_Social_Media(new_data, previous_data):
    differences = [data for data in new_data if data not in previous_data]
    # for data in new_data:
    #     if data not in previous_data:
    #         differences.append(data)
    if differences:
        for difference in differences:
            difference = prettify_msg(difference)
            print(difference)
            Send_Telegram(difference, '-1001694255282')
    else:
        print('No Update!')

def Send_Telegram(msg, chat_id):
    url = 'https://lms-log.davwvod.workers.dev/'
    # payload = {'chat_id': '-1001694255282', 'message_text': 'Your message goes here'}
    payload = {'message_text': msg, 'chat_id': chat_id}
    response = requests.post(url, json=payload)
    print(response.text)

def prettify_msg(msg):
    return f"{msg['User']}:\n{msg['Text']}\n{msg['Attach']}"

def Save_CSV(data, filename):

    # Writing data to CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['User', 'Text', 'Attach']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Write the data rows
        for row in data:
            writer.writerow(row)

    print(f'{len(data)} rows written to {filename} successfully!')

def Load_CSV(filename, token):
    from io import StringIO

    # Personal access token

    # GitHub repository URL
    url = f'https://raw.githubusercontent.com/thewoood/lms-cloud/main/{filename}'

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

    
    
    # if not os.path.isfile(filename):
    #     # Create an empty file if it doesn't exist
    #     with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
    #         pass  # empty code block

    # Reading data from CSV file and storing it in a list of dictionaries
    # data = []
    # with open(filename, mode='r', encoding='utf-8') as csv_file:
    #     reader = csv.DictReader(csv_file)
    #     for row in reader:
    #         data.append(row)

    # print(f'{len(data)} rows loaded from {filename} successfully!')
    # return data

def Upload_Github(username, password, file_name, new_data):

    # Repository details
    repository_name = 'lms-cloud'

    # File details
    csv_data = io.StringIO()
    csv_writer = csv.DictWriter(csv_data, fieldnames=['User', 'Text', 'Attach'])
    csv_writer.writeheader()
    csv_writer.writerows(new_data)

# Read CSV file content
    file_content = csv_data.getvalue()

    # Authenticate with GitHub
    g = Github(username, password)

    # Get the repository
    repo = g.get_user().get_repo(repository_name)

    # Check if the file exists
    try:
        file = repo.get_contents(file_name)
        # Update the existing file
        repo.update_file(file.path, 'Updated!', file_content, file.sha)
        print(f'File "{file_name}" updated successfully.')
    except :
        # Create a new file
        repo.create_file(file_name, 'Created!', file_content)
        print(f'File "{file_name}" created and uploaded successfully.')


def main():
    # Save cookies in cookies.pkl
    SaveCookie('4014013109','1991174322')
        
    urls = ['http://lms.ui.ac.ir/group/84632',
           'http://lms.ui.ac.ir/group/84738',
           'http://lms.ui.ac.ir/group/84675',
           'http://lms.ui.ac.ir/group/84643']
    for url in urls:
        Whats_New(url)

    
    
if __name__ == '__main__':
    main()
    
'''
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
    
    
7) Save date and time of message: .timestamp
8) Send the link of attachment
9) DONE!
    Load data from github
10) Load cookies from github
11) Save cookies to github
12) Restructure the code
    use black.py to pretiffy it
13) since we read csv from github, the returned value is not string and can't be updated
'''
