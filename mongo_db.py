from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


class DbConnect:
    MONGO_BASE_URL = "mongodb+srv://trademql5:trademql5@trademql5.fmlxv.mongodb.net/TradeMQL5?retryWrites=true&w=majority"

    def __init__(self):
        self.connection = MongoClient(self.MONGO_BASE_URL)
        self.db = self.connection['TradeMQL5']

    def get_client(self):
        return self.connection

    def add_rows(self, coll_name, reslt):
        try:
            return self.db[coll_name].insert_one(reslt)
        except ServerSelectionTimeoutError:
            print('ServerSelectionTimeoutError: No connection')

    def find(self, coll_name, query):
        if self.db[coll_name].find_one({"url": query}):
            return True
        else:
            return False

    def close_con(self):
        self.connection.close()
