from deta import Deta
import asyncio

deta = None
db = None

def initialize_db() -> None:
    global deta, db
    deta = Deta()
    db = deta.AsyncBase('lms')

async def put(data: dict, key: str = None) -> dict:
    await db.put(data=data, key=key)

async def put_many(data: list) -> dict:
    """
    Splits data into 25-sized chuncks and
    creates asyncio task
    """
    limit = 25 # Deta put_many limit
    
    # Splitting data into 25-sized chuncks
    chuncks = [data[i: i+limit] for i in range(0, len(data), limit)]
    
    putters = [asyncio.create_task(db.put_many(items=chunck)) for chunck in chuncks]
    responses = asyncio.gather(*putters)
    return responses

async def fetch(query) -> dict:
    response = await db.fetch(query=query)
    return response    

# Public Activity Query
def get_public_activity_query(group: str, user: str, message: str, attachment_text: str,
          attachment_url: str, date: str) -> str:
    """
    Makes Public Activity Query to fetch related data
    """
    query_dict = {
        'group': group,
        'type': 'public_activity', 
        'user': user,
        'message': message,
        'attachment_text': attachment_text,
        'attachment_url': attachment_url,
        'date': date
    }
        
    
    return query_dict