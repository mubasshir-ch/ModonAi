from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

class Database:
    def __init__(self, uri):
        self.cluster = AsyncIOMotorClient(uri)
        self.db = self.cluster["db_name"]
        self.collection = self.db["collection_name"]
