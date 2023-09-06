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
    Splits data into 25-sized chunks and
    creates asyncio task
    """
    limit = 25 # Deta put_many limit
    
    # Splitting data into 25-sized chunks
    chunks = [data[i: i+limit] for i in range(0, len(data), limit)]
    
    putters = [asyncio.create_task(db.put_many(items=chunk)) for chunk in chunks]
    responses = await asyncio.gather(*putters)
    return responses

async def fetch(query: dict) -> list:
    response = await db.fetch(query=query)
    return response.items 

async def detabase_is_empty() -> bool:
    response = await db.fetch(limit=1)
    print(f'response: {response}. Items: {response.items}, Con: {len(response.items)<1}')
    return len(response.items) < 1

async def dict_exists_in_base(query: dict) -> dict:
    '''
    validates the existence of a query in deta base
    if data exists, returns None, else returns data itself 
    '''
    response = await fetch(query)
    return None if bool(response) else query

async def list_of_dicts_exists_in_base(activities: list[dict]) -> list[dict]:
    '''
    based on the implementation of dict_exists_in_base,
    result will only hold new data. old data will become None.
    '''
    validators = [asyncio.create_task(dict_exists_in_base(activity)) for activity in activities]
    result = await asyncio.gather(*validators)
    cleaned_result = list(filter(lambda x: x is not None, result))
    return cleaned_result