import datetime
from uuid import UUID
from fastapi import FastAPI, Header, Request, Response, APIRouter
from pydantic import BaseModel
from ..DBAdmin import DBAdmin

router = APIRouter()

class WebhookResponse(BaseModel):
    result: str

class WebhookData(BaseModel):
    request_id: UUID
    username: str
    event: str
    error: bool = False
    meta: str
    insert: bool = True


db = DBAdmin()

@router.get("/webhook_test")
async def webhook():
    df = db.query('SELECT 1, 2, 3')
    for record in df:
        print(record)
    return {"result": f"DB connection worked fine, returning {len(df)} records"}

@router.post("/webhook", response_model=WebhookResponse, status_code=200)
async def webhook(
    data: WebhookData,
    request: Request,
    response: Response,
):
    if data.insert is True:
        sql = register_event(id=data.request_id, username=data.username, event=data.event, meta=data.meta, error=data.error)
    else:
        sql = update_event(id=data.request_id, meta=data.meta, error=data.error)
    return {"result": sql}


def register_event(id: str, username: str, event: str, meta: str, error: bool = False):
    sql = f'''
        INSERT INTO stylib.__events (id, username, event, error, meta, updated_at)
        VALUES (
            '{id}', '{username}', '{event}', {error}, '{meta}', now()
        )
    '''
    return db.query(sql, commit=True)

def update_event(id: str, meta: str, error: bool = False):
    sql = f'''
        UPDATE stylib.__events
        SET meta = '{meta}', error = {error}, updated_at = now()
        WHERE id = '{id}' 
    '''
    return db.query(sql, commit=True)