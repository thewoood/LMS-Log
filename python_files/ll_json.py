import json
from python_files import ll_deta_drive

def upload_dict(file_name: str, content: dict) -> None:
    dumped_content = json.dumps(content)
    upload_result = ll_deta_drive.upload_file(file_name=file_name, 
                              content=dumped_content,
                              content_type='application/json')
    print(f'----UPLAODED: {upload_result}----')
def download_dict(file_name: str) -> dict:
    raw_content = ll_deta_drive.download_file(file_name)
    
    # ll_deta_drive checks emptieness and availablity of file
    content = json.loads(json.load(raw_content))
    
    return dict(content)
