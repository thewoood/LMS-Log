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

async def fetch(query: dict) -> list:
    response = await db.fetch(query=query)
    return response.items 

async def exists_in_base(query: dict) -> bool:
    '''
    validates the existence of a query in deta base
    '''
    response = await fetch(query)
    return bool(response)