import pymongo
from pymongo import MongoClient, DeleteMany, UpdateMany, errors
from pymongo.errors import *
from os import environ
from bson import json_util
from flask import json

# Mongo Connection Class
class MongoAPI:
    _instance = None
    
    # Singleton Design Pattern to make sure there is only 1 instance created if there are multiple API calls
    @staticmethod
    def getInstance():
        if MongoAPI._instance is None:
            MongoAPI._instance = MongoAPI()
        return MongoAPI._instance
    
    def __init__(self):
        _host = environ.get('MONGO_HOST') or 'localhost'
        _port = environ.get('MONGO_PORT') or 27017
        self.client = MongoClient(_host, int(_port))
    
    # establishing connection with mongo database and collection
    def createConnection(self, data):
        try:
            database = data['database']
            collection = data['collection']
            cursor = self.client[database]
            self.collection = cursor[collection]
            self.data = data
            return True
        except Exception as e:
            return e

    # Reading the records from the database
    def read(self, pageNum: int):
        # pagination
        limit = 25
        skip = limit * (pageNum - 1)
        if pageNum == 1:
            skip = 0
        
        # adding filters if present
        if 'Filter' in self.data:
            where = self.data['Filter']
        else:
            where = {}
        
        # adding sort by if present, otherwise default desc sort will be on priority column
        sortby = []
        if 'Sort' in self.data:
            is_priority_found = True
            for k, v in self.data['Sort'].items():
                if v.strip().lower() == "ascending":
                    v = pymongo.ASCENDING
                else:
                    v = pymongo.DESCENDING
                if k.strip().lower() != "priority":
                    is_priority_found = False
                sortby.append((k, v))
            if not is_priority_found:
                sortby.append(("priority", pymongo.DESCENDING))
        else:
            sortby.append(("priority", pymongo.DESCENDING))
        
        # Read Query Exception Handling
        try:
            documents = self.collection.find(where).sort(sortby).skip(skip).limit(limit)
        except Exception as e:
            return e
        else:
            return json.loads(json_util.dumps(documents))
    
    # Returns number of records on where condition
    def countWhere(self, where):
        if not where:
            where = {}
        
        try:
            count = self.collection.count_documents(where)
        except Exception as e:
            return e
        else:
            return count
    
    # Insert single record in database
    def write(self, data):
        """
        Inserts a record into the collection, with the following fields:
        - "title"
        - "desc"
        - "date"
        - "priority"
        - "status"

        These must be retrieved from the "Document" object.
        """

        new_document = data['Document']
        
        # Write Query Exception Handling
        try:
            response = self.collection.insert_one(new_document)
        except Exception as e:
            return e
        else:
            output = {'Message': 'Record Successfully Inserted', 'Document_ID': str(response.inserted_id)}
            return output
    
    def updateTask(self, task_id, data):
        where = {'_id': task_id}
        updated_data = {'$set': data}

        # Update Query Exception Handling
        try:
            response = self.collection.update_one(where, updated_data)
        except Exception as e:
            return str(e)
        else:
            output = {'Message': 'Successfully Updated {} Records'.format(response.modified_count) if response.modified_count > 0 else 'Nothing was Updated' }
            return output

    # Update a single record in database
    def update(self):
        if 'Filter' in self.data:
            where = self.data['Filter']
        else:
            where = {}
        
        updated_data = {'$set': self.data['Update']}

        # Update Query Exception Handling
        try:
            response = self.collection.update_one(where, updated_data)
        except Exception as e:
            return e
        else:
            output = {'Message': 'Successfully Updated {} Records'.format(response.modified_count) if response.modified_count > 0 else 'Nothing was Updated' }
            return output
    
    # Update multiple records in database
    def bulkUpdate(self):
        if 'Filter' in self.data:
            where = self.data['Filter']
        else:
            where = {}
        updated_data = {'$set': self.data['Update']}
        
        # Bulk Update Query Exception Handling
        try:
            response = self.collection.bulk_write([UpdateMany(where, updated_data)])
        except BulkWriteError as bwe:
            return bwe.details
        else:
            output = {'Message': 'Successfully Updated {} Records'.format(response.modified_count) if response.modified_count > 0 else 'Nothing was Updated' }
        return output
    
    # Delete a single record
    def delete(self, data):
        where = data['Filter']

        # Update Delete Exception Handling
        try:
            response = self.collection.delete_one(where)
        except Exception as e:
            return e
        else:
            output = {'Message': 'Successfully Deleted {} Records'.format(response.deleted_count) if response.deleted_count > 0 else 'Nothing was Deleted' }
            return output
    
    # Delete multiple records
    def bulkDelete(self):
        if 'Filter' in self.data:
            where = self.data['Filter']
        else:
            where = {}
        
        # Bulk Delete Query Exception Handling
        try:
            response = self.collection.bulk_write([DeleteMany(where)])
        except BulkWriteError as bwe:
            return bwe.details
        else:
            output = {'Message': 'Successfully Deleted {} Records'.format(response.deleted_count) if response.deleted_count > 0 else 'Nothing was Deleted' }
            return output
    
    # closing mongo connection on destructor
    def __del__(self):
        self.client.close()
