import pymongo
import sys
import json

client = pymongo.MongoClient('localhost',27017)
db = client['minpaku']
co = db['mocat']

with open('mocat.json') as f:
    df = json.load(f)

result = co.insert_many(df)
print(result)
