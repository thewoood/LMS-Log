from deta import Deta

deta = Deta()
deta_drive = deta.Drive('My_Storage')

def upload_file(file_name: str, content,
                content_type: str = 'application/octet-stram') -> str:
    result = deta_drive.put(name=file_name, 
                            data=content, 
                            content_type=content_type)

    return result

def download_file(file_name: str) -> any:
    content = deta_drive.get(file_name)

    if content:
        return content
    raise FileNotFoundError('!!!!----File Empty/NotFound----!!!!')
