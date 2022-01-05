from fastapi import Request, FastAPI
from pydantic import BaseModel

from datetime import datetime
import httpx

from app.database import verify_login, add_user, get_tickets, insert_ticket, update_ticket

class Operation(BaseModel):
  operations: list

# base template for user.
class User(BaseModel):
  username: str
  password: str

# app initiated.
app = FastAPI()

# sync only data which has started_at in tickets greater than last_sync
last_sync = None

# setting up FastAPI routes.
@app.post('/login', tags=['User'])
async def login(user: User) -> dict:
  user_found = verify_login(user.username, user.password)

  # user found handler.
  if user_found is True:
      return {
        'error_id': 0,
        'error_message': 'success'
      }
  return {
    'error_id': 404,
    'error_message': 'user not found'
  }


@app.post('/register', tags=['User'])
async def register(user: User) -> dict:
  user_added = add_user(user.username, user.password)

  # user found handler.
  if user_added is True:
    return {
      'error_id': 0,
      'error_message': 'success'
    }
  return {
    'error_id': 400,
    'error_message': 'user not added'
  }


# get all opened tickets.
# pass is_closed=True to get all closed tickets too.
@app.get('/tickets', tags=['Tickets Management'])
async def list_tickets(is_closed: str) -> list:
  if is_closed.lower()=='true': return get_tickets(True)
  return get_tickets(False)


@app.post('/tickets', tags=['Tickets Management'])
async def refresh_tickets() -> dict:
  response=httpx.get('http://solar_power:5000/')
  tickets=response.json()['data']
  global last_sync
  
  # for each ticket, add it into mongo database.
  # filter out data which have started_at greater than last_sync
  for ticket in tickets:
    started_at=datetime.fromisoformat(ticket['started_at'])
    if last_sync is None or started_at > last_sync: insert_ticket(ticket=ticket)
  
  # update last_sync to newer time
  last_sync = datetime.now()
  return {
    'error_id': 0,
    'error_message': 'success'
  }

# add maintenance operations for given ticket id.
@app.put('/ticket/{id}', tags=['Tickets Management'])
async def close_tickets(id: str, operations: Operation) -> dict:
  update_ticket(id, operations)
  return {
    'error_id': 0,
    'error_message': 'success'
  }
