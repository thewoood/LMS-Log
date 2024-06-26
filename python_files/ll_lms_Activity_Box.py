from bs4 import BeautifulSoup

EMPTY_PLACE_HOLDER = 'empty'

class Msg_Box():
    def __init__(self, sub_soup: BeautifulSoup, css_selectors: dict, group: str) -> None:
        self.group = group
        self.sub_soup = sub_soup
        self.css_selectors = css_selectors

    def select_user(self) -> str:
        user = self.sub_soup.select_one(self.css_selectors['user'])
        user = user.text.strip().replace('\n\n', '')
        user = EMPTY_PLACE_HOLDER if bool(user) == False else user
        return user

    def select_message(self) -> str:
        message = self.sub_soup.select_one(self.css_selectors['message'])
        message = '' if message is None else message.text
        message = message.strip().replace('\n\n', '')
        # when author sends no message, there is actually a message being
        # sent. but i failed to recognize the value of it so i ended up
        # using bool(message)
        message = EMPTY_PLACE_HOLDER if bool(message) == False else message
        return message
    
    def select_attachment_text(self) -> str:
        attachment = self.sub_soup.select_one(self.css_selectors['attachment'])
        attachment_text = '' if attachment is None else attachment.text
        attachment_text = attachment_text.strip().replace('\n\n', '')
        attachment_text = EMPTY_PLACE_HOLDER if bool(attachment_text) == False else attachment_text
        return attachment_text
        
    def select_attachment_url(self) -> str:
        attachment = self.sub_soup.select_one(self.css_selectors['attachment'])
        attachment_url = f'https://lms.ui.ac.ir{attachment.find("a")["href"]}' if attachment != None else ''
        attachment_url = EMPTY_PLACE_HOLDER if bool(attachment_url) == False else attachment_url
        return attachment_url
        
    def select_time(self) -> str:
        feed_item_date = self.sub_soup.find('div', class_='feed_item_date')
        timestamp_span = feed_item_date.find('span', class_='timestamp')
        time_str = timestamp_span['title'] # type: ignore
        time_str = time_str.strip().replace('\n\n', '')
        time_str = EMPTY_PLACE_HOLDER if bool(time_str) == False else time_str
        return time_str
    
    def setup_msg(self,) -> dict:
        user = self.select_user()
        message = self.select_message()
        attachment_text = self.select_attachment_text()
        attachment_url = self.select_attachment_url()
        time = self.select_time()

        msg = {
            'group': self.group,
            'type': 'activity', 
            'user': user,
            'message': message,
            'attachment_text': attachment_text,
            'attachment_url': attachment_url,
            'date': time,
        }

        return msg