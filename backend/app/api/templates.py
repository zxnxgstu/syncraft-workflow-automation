from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models import User

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])

TEMPLATES = [
    {"id":"webhook-alert","name":"Webhook Alert Pipeline","category":"Notifications","description":"Receive a webhook, enrich the payload and create an alert preview.","trigger_type":"webhook","steps":[
        {"position":0,"step_type":"trigger","name":"Incoming webhook","config":{"source":"webhook"}},
        {"position":1,"step_type":"transform","name":"Add metadata","config":{"set":{"source":"external","handled_by":"Syncraft"}}},
        {"position":2,"step_type":"telegram","name":"Telegram alert","config":{"message":"New event: {{message}}"}}]},
    {"id":"api-sync","name":"API Data Sync","category":"Data","description":"Call a REST API on demand and keep the response in the execution output.","trigger_type":"manual","steps":[
        {"position":0,"step_type":"trigger","name":"Manual trigger","config":{}},
        {"position":1,"step_type":"http","name":"Fetch API","config":{"method":"GET","url":"https://jsonplaceholder.typicode.com/todos/1","timeout":8}},
        {"position":2,"step_type":"log","name":"Write audit log","config":{"message":"API sync completed"}}]},
    {"id":"scheduled-report","name":"Scheduled Report","category":"Operations","description":"Prepare a scheduled report payload and log completion.","trigger_type":"schedule","schedule_minutes":60,"steps":[
        {"position":0,"step_type":"trigger","name":"Hourly schedule","config":{}},
        {"position":1,"step_type":"transform","name":"Build report metadata","config":{"set":{"report":"hourly","generated":True}}},
        {"position":2,"step_type":"log","name":"Report ready","config":{"message":"Scheduled report is ready"}}]},
]


@router.get("")
def list_templates(_: User = Depends(get_current_user)):
    return TEMPLATES
