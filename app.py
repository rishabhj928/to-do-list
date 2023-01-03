
from flask import Flask, abort, request, json, Response, redirect
from bson import json_util
from os import environ
from bulk_tasks import bulkupdatee
from mongoapi import MongoAPI
from collections import defaultdict

from celery.result import AsyncResult

app = Flask(__name__)

# custom response message handler
def customResponse(message, status):
    if status == 200:
        resp = {"Status": "Success", "data": message}
    elif status == 400:
        resp = {"Status": "Error", "Message": message}
    else:
        resp = message
    return Response(response=json.dumps(resp, indent=4), status=200, mimetype='application/json')

@app.route("/task", methods=['GET'], defaults={'pageNum': 1})
@app.route("/task/<int:pageNum>", methods=['GET'])
def getTask(pageNum):
    # List all Tasks Available, through pageNum the pagination is done.
    if pageNum < 1:
        pageNum = 1
    data = request.json
    if data is None or data == {}:
        return customResponse("Please provide connection info", 400)
    
    mongo_obj = MongoAPI.getInstance()
    # print(mongo_obj)
    conn = mongo_obj.createConnection(data)

    # Mongo Connection Exception Handling
    if isinstance(conn, Exception):
        return customResponse(str(conn), 400)
    else:
        # Read Query Exception Handling
        response_data = mongo_obj.read(pageNum)
        if isinstance(response_data, Exception):
            return customResponse(str(response_data), 400)
        else:
            return customResponse(response_data, 200)

@app.route("/task/add", methods=['POST'])
def addTask():
    # Add a new Task
    data = request.json
    if data is None or data == {} or 'Document' not in data:
        return customResponse("Please provide connection info and Document object", 400)
    
    doc = data['Document']

    # validations
    error_message = []
    valid = True
    if 'title' not in doc:
        error_message.append("Please enter title.")
        valid = False
    elif len(doc['title']) > 100:
        error_message.append("Title length must be less than 100 characters.")
        valid = False
    
    if 'desc' not in doc:
        error_message.append("Please enter Description.")
        valid = False
    elif len(doc['desc']) > 500:
        error_message.append("Description length must be less than 500 characters.")
        valid = False
    
    if 'priority' not in doc:
        error_message.append("Please enter Priority.")
        valid = False
    elif doc['priority'].strip().lower() not in ['high', 'medium', 'low']:
        error_message.append("Priority must be High/Medium/Low")
        valid = False
    
    if 'status' not in doc:
        error_message.append("Please enter Status.")
        valid = False
    elif doc['status'].strip().lower() not in ['pending', 'completed']:
        error_message.append("Status must be Pending/Completed")
        valid = False
    
    if not valid and len(error_message) > 0:
        return customResponse(error_message, 400)
    

    mongo_obj = MongoAPI.getInstance()
    conn = mongo_obj.createConnection(data)

    # Mongo Connection Exception Handling
    if isinstance(conn, Exception):
        return customResponse(str(conn), 400)
    else:
        # checking if the task is already created, with exception handling
        count_records = mongo_obj.countWhere({"title": doc['title']})
        if isinstance(count_records, Exception):
            return customResponse(str(response_data), 400)
        else:
            if count_records > 0:
                message = "{} already exists, please create another task".format(doc['title'])
                return customResponse(message, 400)
        
        # Write Query Exception Handling
        response_data = mongo_obj.write(data)
        if isinstance(response_data, Exception):
            return customResponse(str(response_data), 400)
        else:
            return customResponse(response_data, 200)

@app.route("/task/edit", methods=['PUT'])
def editTask():
    # Edit a task
    data = request.json
    if data is None or data == {} or 'Update' not in data:
        return customResponse("Please provide connection info and Update object", 400)
    
    doc = data['Update']

    # validations
    error_message = []
    valid = True
    if 'title' in doc and len(doc['title']) > 100:
        error_message.append("Title length must be less than 100 characters.")
        valid = False
    
    if 'desc' in doc and len(doc['desc']) > 500:
        error_message.append("Description length must be less than 500 characters.")
        valid = False
    
    if 'priority' in doc and doc['priority'].strip().lower() not in ['high', 'medium', 'low']:
        error_message.append("Priority must be High/Medium/Low")
        valid = False
    
    if 'status' in doc and doc['status'].strip().lower() not in ['pending', 'completed']:
        error_message.append("Status must be Pending/Completed")
        valid = False
    
    if not valid and len(error_message) > 0:
        return customResponse(error_message, 400)
    
    mongo_obj = MongoAPI.getInstance()
    # print(mongo_obj)
    conn = mongo_obj.createConnection(data)

    # Mongo Connection Exception Handling
    if isinstance(conn, Exception):
        return customResponse(str(conn), 400)
    else:
        # checking if the task is already created, with exception handling
        count_records = mongo_obj.countWhere({"title": doc['title']})
        if isinstance(count_records, Exception):
            return customResponse(str(response_data), 400)
        else:
            if count_records > 0:
                message = "{} already exists, please choose another task".format(doc['title'])
                return customResponse(message, 400)
                
        # Update Query Exception Handling
        response_data = mongo_obj.update()
        if isinstance(response_data, Exception):
            return customResponse(str(response_data), 400)
        else:
            return customResponse(response_data, 200)

@app.route("/task/bulkedit", methods=['PUT'])
def bulkEditTask():
    # Bulk edit tasks
    data = request.json
    if data is None or data == {} or 'Update' not in data:
        return customResponse("Please provide connection info and Update object", 400)
    
    # validate title based on filters if present
    if 'title' in data['Update']:
        return customResponse("Can't update same title for multiple documents, please bulk update any other field", 400)

    
    mongo_obj = MongoAPI.getInstance()
    # print(mongo_obj)
    conn = mongo_obj.createConnection(data)
    
    # Mongo Connection Exception Handling
    if isinstance(conn, Exception):
        return customResponse(str(conn), 400)
    else:
        # Bulk Update Query Exception Handling
        response_data = mongo_obj.bulkUpdate()
        if isinstance(response_data, Exception):
            return customResponse(str(response_data), 400)
        else:
            return customResponse(response_data, 200)

@app.route("/task/delete", methods=['DELETE'])
def deleteTask():
    # Delete a task
    data = request.json
    if data is None or data == {} or 'Filter' not in data:
        return customResponse("Please provide connection info and Filter object", 400)
    
    mongo_obj = MongoAPI.getInstance()
    # print(mongo_obj)
    conn = mongo_obj.createConnection(data)
    
    # Mongo Connection Exception Handling
    if isinstance(conn, Exception):
        return customResponse(str(conn), 400)
    else:
        # Delete Query Exception Handling
        response_data = mongo_obj.delete(data)
        if isinstance(response_data, Exception):
            return customResponse(str(response_data), 400)
        else:
            return customResponse(response_data, 200)

@app.route("/task/bulkdelete", methods=['DELETE'])
def bulkDeleteTask():
    # Bulk delete tasks
    data = request.json
    if data is None or data == {}:
        return customResponse("Please provide connection info", 400)
    
    mongo_obj = MongoAPI.getInstance()
    # print(mongo_obj)
    conn = mongo_obj.createConnection(data)
    
    # Mongo Connection Exception Handling
    if isinstance(conn, Exception):
        return customResponse(str(conn), 400)
    else:
        # Delete Query Exception Handling
        response_data = mongo_obj.bulkDelete()
        if isinstance(response_data, Exception):
            return customResponse(str(response_data), 400)
        else:
            return customResponse(response_data, 200)

@app.route('/celeryupdate', methods=['POST'])
def celeryInsert():
    data = request.json
    if data is None or data == {} or 'bulk_ids' not in data or 'Update' not in data:
        return customResponse("Please provide connection info, bulk_ids object and Update object", 400)
    
    bulk_ids = data['bulk_ids']
    updated_data = data['Update']

    # mongo_obj = MongoAPI.getInstance()
    # conn = mongo_obj.createConnection(data)
    
    # validate title based on filters if present
    if 'title' in data['Update']:
        return customResponse("Can't update same title for multiple documents, please bulk update any other field", 400)
        
    task_result = defaultdict(list)
    for task_id in bulk_ids:
        task_status = bulkupdatee.delay(task_id, updated_data)
        task_result[task_id].append(task_status.status)
    
    return customResponse(task_result, 200)
    
if __name__ == "__main__":
    _debug = environ.get('DEBUG') or True
    app.run(debug=_debug)
