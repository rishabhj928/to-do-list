
## Task Management Application
- Language: Python
- Framework: Flask
- Database: MongoDB

### API Endpoints:

- **GET**⠀`/task`
List all the tasks available

Optional objects can be added like:
```
Sort: {
    "title": "ascending",
    "status": "descending"
}
```
```
"Filter": {
    "title": "Task 1"
}
```
We can even add multiple filters for same column using $in like:
```
"Filter": {
    "title": {
        "$in": ["Task 1", "Task 2"]
    },
    "status": "pending"
}
```


- **POST**⠀`/task/add`
Create a new Task
```
{
    "database": "db_name",
    "collection": "collection_name",
    "Document": {
        "title": "Task 1",
        "desc": "Task 1 description",
        "date": "2022-12-16",
        "priority": "high",
        "status": "pending"
    }
}
```

- **PUT**⠀`/task/edit`
Edit an existing task
```
{
    "database": "db_name",
    "collection": "collection_name",
    "Filter": {
        "title": "Task 1"
    },
    "Update": {
        "desc": "task",
        "priority": "high"
    }
}
```

- **PUT**⠀`/task/bulkedit`
Bulk edit the tasks

```
{
    "database": "db_name",
    "collection": "collection_name",
    "Filter": {
        "title": {
            "$in": [
                "Task 1",
                "Task 2"
            ]
        }
    },
    "Update": {
        "status": "completed"
    }
}
```

- **DELETE**⠀`/task/delete`
Delete a task

```
{
    "database": "db_name",
    "collection": "collection_name",
    "Filter": {
        "title": "Task 3"
    }
}
```

- **DELETE**⠀`/task/bulkdelete`
Bulk Delete multiple tasks
```
{
    "database": "test",
    "collection": "posts"
}
```
or we can specify Filters as well
```
{
    "database": "db_name",
    "collection": "collection_name",
    "Filter": {
        "title": "Task 3"
    }
}
```