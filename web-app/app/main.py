from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from bson import ObjectId

from datetime import datetime
import httpx

from os import system, path
from app.database import save, fetch

IMAGE_DIR='imgs'
OUTPUT_DIR='output'

# app initiated.
app = FastAPI()

# setting up FastAPI routes.
@app.post('/upload', tags=['Assessment'])
async def upload(bk: BackgroundTasks, image: UploadFile = File(...)) -> dict:
  
  # new id for incoming record.
  id = ObjectId()
  file_name = '{}.jpeg'.format(id)
  image.filename = file_name
  contents_before = image.file.read()
  with open('{}'.format(path.abspath(IMAGE_DIR)), 'wb+') as f:
    f.write(contents_before)
  
  # background task.
  bk.add_task(inference, id, contents_before, file_name, path.abspath(IMAGE_DIR), path.abspath('../../docs/best.pt'))
  
  # let client know WIP in progress.
  return {
    'status': '200',
    'resource_id': id,
    'message': 'WIP. Use FetchById to check completition status.'
  }


# inference method.
def inference(id, contents_before, file_name, source_path, weights_path):
  system('docker run --rm --ipc=host -v {}:/data/best.pt:rw -v {}:/data/imgs:rw -v {}:/usr/src/app/runs/detect:rw  ultralytics/yolov5:latest python detect.py --weights /data/best.pt --img 4000 --conf 0.25 --source /data/imgs --save-txt --hide-label'.format(weights_path, source_path, path.abspath(OUTPUT_DIR)))
  
  contents_after, labels_list = None, []
  with open('{}/{}'.format(path.abspath(OUTPUT_DIR)), 'rb+') as f:
    contents_after = f.read()
  
  # read labels.
  with open('{}/exp/{}.txt'.format(path.abspath(OUTPUT_DIR), file_name.split('.')[0]), 'rb+') as f:
    labels_file = f.read()
    for labels in labels_file:
      labels_list.append(labels.split(' '))
  
  # save into mongo.
  save(id, contents_before, contents_after, labels)

@app.get('/fetch/{id}', tags=['Assessment'])
async def fetch(id: str) -> dict:
  record = fetch(id)

  # user found handler.
  if record is None:
    return {
      'status': 301,
      'message': 'Acknowledge. Processing WIP. Check Logs in terminal or stdout.'
    }
  return {
    'id': record['_id'],
    'labels': record['labels']
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
