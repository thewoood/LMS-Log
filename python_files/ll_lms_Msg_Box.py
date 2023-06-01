from bs4 import BeautifulSoup

class Msg_Box():
    def __init__(self, sub_soup: BeautifulSoup, css_selectors: dict) -> None:
        self.sub_soup = sub_soup
        self.css_selectors = css_selectors

    def slct_user(self) -> str:
        user = self.sub_soup.select_one(self.css_selectors['user'])
        user = user.text.strip().replace('\n\n', '')
        return user

    def slct_message(self) -> str:
        message = self.sub_soup.select_one(self.css_selectors['message'])
        message = '' if message is None else message.text
        message = message.strip().replace('\n\n', '')
        return message
    
    def slct_attachment_text(self) -> str:
        attachment = self.sub_soup.select_one(self.css_selectors['attachment'])
        attachment_text = '' if attachment is None else attachment.text
        attachment_text = attachment_text.strip().replace('\n\n', '')
        return attachment_text
        
    def slct_attachment_url(self) -> str:
        attachment = self.sub_soup.select_one(self.css_selectors['attachment'])
        attachment_url = f'https://lms.ui.ac.ir{attachment.find("a")["href"]}' if attachment != None else ''
        return attachment_url
        
    def slct_time(self) -> str:
        feed_item_date = self.sub_soup.find('div', class_='feed_item_date')
        timestamp_span = feed_item_date.find('span', class_='timestamp')
        time_str = timestamp_span['title']
        time_str = time_str.strip().replace('\n\n', '')
        return time_str
    
    def setup_msg(self,) -> dict:
        user = self.slct_user()
        message = self.slct_message()
        attachment_text = self.slct_attachment_text()
        attachment_url = self.slct_attachment_url()
        time = self.slct_time()

        msg = {
            'user': user,
            'message': message,
            'attachment_text': attachment_text,
            'attachment_url': attachment_url,
            'date': time,
               }

        return msg