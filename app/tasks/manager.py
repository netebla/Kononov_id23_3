import uuid
import redis
import json

# Статусы задач
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def create_task() -> str:
    task_id = str(uuid.uuid4())
    task_data = {
        "status": STATUS_RUNNING,
        "progress": 0,
        "result": None
    }
    r.set(task_id, json.dumps(task_data))
    return task_id

def update_task(task_id, status=None, progress=None, result=None):
    task_data = r.get(task_id)
    
    if task_data:
        task_data = json.loads(task_data)
    else:
        task_data = {"status": STATUS_RUNNING, "progress": 0, "result": None}
    
    if status is not None:
        task_data["status"] = status
    if progress is not None:
        task_data["progress"] = progress
    if result is not None:
        task_data["result"] = result

    r.set(task_id, json.dumps(task_data))

def get_task(task_id: str) -> dict:
    task_data = r.get(task_id)
    if task_data:
        return json.loads(task_data)
    else:
        return {"status": "unknown", "progress": 0, "result": None}