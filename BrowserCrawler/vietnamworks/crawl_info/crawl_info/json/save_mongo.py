import pymongo
import json
import pymongo.mongo_client
import os

def save_mongo(uri = "mongodb+srv://miruku2201:naM0329601106@cluster0.obezhgu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
                db = None,
                collection = None,
                data = None
            ) -> str:
    myclient = pymongo.mongo_client.MongoClient(uri)
    if myclient:
        print("Connected to MongoDB")
    else:
        return "Error: Can't connect to MongoDB"
    
    if db is None or collection is None or data is None:
        return "Error: Missing parameters"
    
    mydb = myclient[db]
    mycol = mydb[collection]
    mycol.insert_many(data)
    return "Success"

def read_json(filenamepath: str = None):
    if filenamepath is None:
        return "Error: Missing parameters"
    
    with open(filenamepath, "r", encoding="utf8") as f:
        data = json.load(f)
        return data

if __name__ == "__main__":
    data = read_json("json/out.json")
    print(save_mongo(db="Jobs", collection="vietnamworks", data=data))