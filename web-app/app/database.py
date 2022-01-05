
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId


client=MongoClient('mongodb://root:admin3311@localhost:27017/store?authSource=admin')
database=client['store']

# save into mongodb
def save(id, image, inference_image, labels) -> bool:
  
  # get collection cursor.
  store_collection=database['store']
  store_collection.insert_one({
    '_id': ObjectId(id),
    'image': image,
    'inference_image': image,
    'labels': labels,
    'timestamp': datetime.now().isoformat()
  })
  return True


# return one record from mongodb.
def fetch(id):
  
  # get collection cursor.
  items_collection=database['store']
  print('----------INSIDE', id)

  # only return tickets where operations not submitted.
  items = items_collection.find()
  for item in items:
    if item['_id'] == ObjectId(id):
      return item
  return None