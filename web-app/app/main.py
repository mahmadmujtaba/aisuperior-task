from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from bson import ObjectId

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
  with open('{}/{}'.format(path.abspath(IMAGE_DIR), file_name), 'wb') as f:
    f.write(contents_before)
  
  # background task.
  bk.add_task(inference, str(id), contents_before, file_name, path.abspath(IMAGE_DIR), path.abspath('../docs/best.pt'))
  
  # let client know WIP in progress.
  return {
    'status': 301,
    'resource_id': str(id),
    'message': 'WorkInProgress. Use ResourceId to check completition status in FetchApi.'
  }


# inference method.
def inference(id, contents_before, file_name, source_path, weights_path):
  print('docker run --rm --ipc=host -v {}:/data/best.pt:rw -v {}:/data/imgs:rw -v {}:/usr/src/app/runs/detect:rw  ultralytics/yolov5:latest python detect.py --weights /data/best.pt --img 4000 --conf 0.25 --source /data/imgs --save-txt --hide-label'.format(weights_path, source_path, path.abspath(OUTPUT_DIR)))
  system('docker run --rm --ipc=host -v {}:/data/best.pt:rw -v {}:/data/imgs:rw -v {}:/usr/src/app/runs/detect:rw  ultralytics/yolov5:latest python detect.py --weights /data/best.pt --img 4000 --conf 0.25 --source /data/imgs --save-txt --hide-label'.format(weights_path, source_path, path.abspath(OUTPUT_DIR)))
  
  contents_after, labels_list = None, []
  with open('{}/{}'.format(path.abspath(OUTPUT_DIR)), 'rb') as f:
    contents_after = f.read()
  
  # read labels.
  with open('{}/exp/{}.txt'.format(path.abspath(OUTPUT_DIR), file_name.split('.')[0]), 'rb+') as f:
    labels_file = f.read()
    for labels in labels_file:
      labels_list.append(labels.split(' '))
  
  # save into mongo.
  save(id, contents_before, contents_after, labels)
  return {
    'status': 'ok'
  }

@app.get('/fetch/{resource_od}', tags=['Assessment'])
async def fetch(resource_od: str) -> dict:
  record = fetch(resource_od)

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
