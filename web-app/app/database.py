
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId


client=MongoClient('mongodb://root:admin3311@mongodb:27017/tickets?authSource=admin')
database=client['tickets']

# get all users from mongodb.
def verify_login(username, password) -> bool:
  
  # if collection is not present, then return no users.
  if 'users' not in database.list_collection_names(): return False
  
  # get collection cursor.
  users_collection=database['users']
  user=users_collection.find_one({
    'username': username,
    'password': password
  })
  
  # if user is found, return true else false.
  if user is not None: return True
  return False

# add new user into mongodb.
def add_user(username, password) -> bool:
  
  # get collection cursor.
  users_collection=database['users']
  user=users_collection.find_one({
    'username': username,
    'password': password
  })
  
  # if user not found, add it to database.
  if user is None:
    users_collection.insert_one({
      'username': username,
      'password': password
    })
    return True
  
  # return false to show user is already present.
  return False


# return all tickets from mongodb.
def get_tickets(is_closed) -> list:
  
  # get collection cursor.
  tickets_collection=database['tickets']
  
  # change _id to id for each document.
  tickets2 = []
  if is_closed is True:
    tickets = tickets_collection.find()
    for ticket in tickets:
      if 'operations' in list(ticket.keys()): ticket['status']='resolved'
      else: ticket['status']='pending'
      ticket['id']=str(ticket['_id'])
      ticket.pop('_id', None)
      tickets2.append(ticket)
  else:
    # only return tickets where operations not submitted.
    tickets = tickets_collection.find({ 'operations': { '$exists': False } })
    for ticket in tickets:
      ticket['status']='pending'
      ticket['id']=str(ticket['_id'])
      ticket.pop('_id', None)
      tickets2.append(ticket)
  return tickets2

# find one ticket by id.
def get_one_ticket(id) -> dict:
  
  # get collection cursor.
  tickets_collection=database['tickets']
  return tickets_collection.find_one({'_id': id})

# add ticket into mongodb.
def insert_ticket(ticket) -> bool:
  
  # get collection cursor.
  tickets_collection=database['tickets']
  tickets_collection.insert_one(ticket)
  return True

# updates a ticket within mongodb.
def update_ticket(id, operations) -> bool:
  
  # get collection cursor.
  tickets_collection=database['tickets']
  tickets_collection.find_one_and_update({
      '_id': ObjectId(id)
    }, {
      '$set': {
        'operations': str(operations),
        'resolved_at': datetime.now()
      }
    },
    upsert=False
  )
  return True