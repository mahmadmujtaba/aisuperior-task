
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
    'inference_image': inference_image,
    'labels': labels,
    'timestamp': datetime.now().isoformat()
  })
  return True


# return one record from mongodb.
def fetch_data(id)->dict:
  
  # get collection cursor.
  items_collection=database['store']

  # only return tickets where operations not submitted.
  return items_collection.find_one(ObjectId(id))