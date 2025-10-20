"""
db module
uses pymongo
includes startup
"""

import os
import pymongo
from dotenv import load_dotenv
from bson.objectid import ObjectId


def db_connect():
    load_dotenv()



    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("MONGO_DBNAME")]

    cxn.admin.command("ping")
    print(" *", "Connected to db:", os.getenv("MONGO_DBNAME"))
    return db
    


if __name__ == "__main__":
    db = db_connect()
    print(db)
