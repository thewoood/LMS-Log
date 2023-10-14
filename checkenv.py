from dotenv import load_dotenv
import os 

ENVs = [
    'LMS_USERNAME',
    'LMS_PASSWORD',
    'CHAT_IDs'
]

class EnvNotSet(Exception):
    pass

def check_env():
    load_dotenv()
    for env in ENVs:
        value = os.getenv(env)
        if not value:
            raise EnvNotSet(f'Please set {env} via SETTINGS -> CONFIGURATION in Deta.')
        
if __name__ == '__main__':
    check_env()