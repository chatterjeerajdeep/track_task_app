from constants import Constants
from pymongo import MongoClient

class MongoDBServices():
    def __init__(self):
        mongodburl = Constants.DB_URL
        self.client_mongo = MongoClient(mongodburl)

    def insert_document(self, collection_name, query):
        db_obj =self.client_mongo[Constants.APP_DATABASE]
        collection = db_obj[collection_name]
        doc = collection.insert_one(query)
        return doc

    def load_documents(self, collection_name, query):
        db_obj = self.client_mongo[Constants.APP_DATABASE]
        collection = db_obj[collection_name]
        doc = collection.find(query)
        return doc

    def delete_documents(self, collection_name, query):
        db_obj = self.client_mongo[Constants.APP_DATABASE]
        collection = db_obj[collection_name]
        doc = collection.delete_many(query)
        return doc

    def update_documents(self,collection_name, query, new_value):
        db_obj = self.client_mongo[Constants.APP_DATABASE]
        collection = db_obj[collection_name]
        new_values = {"$set": new_value}
        doc = collection.delete_many(query, new_values)
        return doc
