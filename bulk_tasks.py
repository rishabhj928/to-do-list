import os
from mongoapi import MongoAPI
from celery import Celery
import celeryconfig
from pymongo import MongoClient

# os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

broker_url = 'amqp://rishabh:password@localhost:5672/task_host'
backend_url = 'rpc://'
# celery_obj = Celery(__name__, broker=broker_url, backend=backend_url, accept_content=["json","pickle","yaml"], task_serializer='pickle')
celery_obj = Celery(__name__, broker=broker_url, accept_content=["json","pickle","yaml"], task_serializer='json', result_serializer='json')
celery_obj.config_from_object(celeryconfig)

@celery_obj.task
def bulkupdatee(task_id, data):
    with MongoClient('mongodb://localhost:27017') as connection:
        db = connection.test
        db.posts.update_one({'_id': task_id}, {'$set': data})
    return True
