"""
db module
uses pymongo
includes startup
"""

import pymongo
from bson.objectid import ObjectId
import datetime
import os
from dotenv import load_dotenv


def dbConnect():
    load_dotenv()

    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("MONGO_DBNAME")]

    try:
        cxn.admin.command("ping")
        print(" *", "Connected to MongoDB!")
    except Exception as e:
        print(" * MongoDB connection error:", e)

    return db