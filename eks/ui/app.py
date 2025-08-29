import os
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
import uvicorn
import gradio as gr
import httpx
import oauth
import uuid
import asyncio
from typing import Dict

from dotenv import load_dotenv
load_dotenv()  # take environment variables

AGENT_UI_ENDPOINT_URL_1 = os.getenv("AGENT_UI_ENDPOINT_URL_1", "http://localhost:3000/prompt")
AGENT_UI_ENDPOINT_URL_2 = os.getenv("AGENT_UI_ENDPOINT_URL_2", "http://localhost:4000/prompt")
BASE_URL = os.getenv("BASE_URL","http://localhost:8000")
BASE_PATH = os.getenv("BASE_PATH","/")
# check if BASE_PATH is empty string and set to "/"
if BASE_PATH == "":
    BASE_PATH = "/"
CHAT_PATH = os.getenv("CHAT_PATH", "/chat")

# the following urls if BASE_PATH is / then another / after BASE_PATH is not need it
CHAT_UI_URL = f"{BASE_URL}{BASE_PATH}{'chat/' if BASE_PATH.endswith('/') else '/chat/'}" #important this url need to end with /
UI_URL = f"{BASE_URL}{BASE_PATH}{'' if BASE_PATH.endswith('/') else '/'}" #important this url needs to end with /
LOGIN_URL = f"{BASE_URL}{BASE_PATH}{'login' if BASE_PATH.endswith('/') else '/login'}"
LOGOUT_URL = f"{BASE_URL}{BASE_PATH}{'logout' if BASE_PATH.endswith('/') else '/logout'}"
OAUTH_CALLBACK_URI = f"{BASE_URL}{BASE_PATH}{'callback' if BASE_PATH.endswith('/') else '/callback'}"

print(f"AGENT_UI_ENDPOINT_URL_1:{AGENT_UI_ENDPOINT_URL_1}")
print(f"AGENT_UI_ENDPOINT_URL_2:{AGENT_UI_ENDPOINT_URL_2}")
print(f"BASE_URL:{BASE_URL}")
print(f"BASE_PATH:{BASE_PATH}")
print(f"CHAT_PATH:{CHAT_PATH}")
print(f"UI_URL:{UI_URL}")
print(f"CHAT_UI_URL:{CHAT_UI_URL}")
print(f"LOGIN_URL:{LOGIN_URL}")
print(f"LOGOUT_URL:{LOGOUT_URL}")
print(f"OAUTH_CALLBACK_URI:{OAUTH_CALLBACK_URI}")


user_avatar = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
bot_avatar = "https://cdn-icons-png.flaticon.com/512/4712/4712042.png"

# Store for background tasks
background_tasks: Dict[str, Dict] = {}

fastapi_app = FastAPI()

fastapi_app.add_middleware(SessionMiddleware, secret_key="secret")
oauth.add_oauth_routes(
    fastapi_app,
    OAUTH_CALLBACK_URI=OAUTH_CALLBACK_URI,
    UI_URL=UI_URL
    )

@fastapi_app.get("/")
async def root():
    print(f"🏠 Root endpoint accessed redirecting to {CHAT_UI_URL}")
    return RedirectResponse(url=CHAT_UI_URL)

def check_auth(req: Request):
    if not "access_token" in req.session or not "username" in req.session:
        print(f"check_auth:: access_token not found or username not found, redirecting to {LOGIN_URL}")
        raise HTTPException(status_code=302, detail="Redirecting to login", headers={"Location": LOGIN_URL})

    username = req.session["username"]

    print(f"check_auth::auth found username: {username}")
    return username

# Background task processing functions
@fastapi_app.post("/start-chat")
async def start_chat_task(request: Request):
    # Check authentication first
    if not "access_token" in request.session or not "username" in request.session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    data = await request.json()
    task_id = str(uuid.uuid4())
    
    # Store task info
    background_tasks[task_id] = {
        "status": "processing",
        "result": None,
        "error": None
    }
    
    # Start background task
    asyncio.create_task(process_chat_background(task_id, data))
    
    return {"task_id": task_id}

@fastapi_app.get("/chat-status/{task_id}")
async def get_chat_status(task_id: str):
    if task_id not in background_tasks:
        return {"status": "not_found"}
    return background_tasks[task_id]

@fastapi_app.delete("/cleanup-old-tasks")
async def cleanup_old_tasks():
    """Clean up tasks older than 1 hour to prevent memory leaks"""
    import time
    current_time = time.time()
    tasks_to_remove = []
    
    for task_id, task_data in background_tasks.items():
        # If task has been around for more than 1 hour, remove it
        # This is a simple cleanup - in production you'd want timestamps
        if len(background_tasks) > 100:  # Simple cleanup when too many tasks
            tasks_to_remove.append(task_id)
    
    for task_id in tasks_to_remove[:50]:  # Remove oldest 50 tasks
        del background_tasks[task_id]
    
    return {"cleaned_up": len(tasks_to_remove)}

async def process_chat_background(task_id: str, data: dict):
    try:
        message = data["message"]
        agent_mode = data["agent_mode"]
        token = data["token"]
        
        # Select endpoint based on agent mode
        if agent_mode == "Single Agent(Weather)":
            endpoint_url = AGENT_UI_ENDPOINT_URL_1
            print(f"Background task {task_id}: Using Single Agent(Weather) endpoint: {endpoint_url}")
        else:  # Multi-Agent(Travel)
            endpoint_url = AGENT_UI_ENDPOINT_URL_2
            print(f"Background task {task_id}: Using Multi-Agent(Travel) endpoint: {endpoint_url}")

        async with httpx.AsyncClient(timeout=httpx.Timeout(600.0, connect=30.0)) as client:
            agent_response = await client.post(
                endpoint_url,
                headers={"Authorization": f"Bearer {token}"},
                json={"text": message}
            )

            if agent_response.status_code == 401 or agent_response.status_code == 403:
                background_tasks[task_id] = {
                    "status": "failed",
                    "result": None,
                    "error": f"Agent returned authorization error. Status code: {agent_response.status_code}"
                }
                return

            if agent_response.status_code != 200:
                background_tasks[task_id] = {
                    "status": "failed",
                    "result": None,
                    "error": f"Failed to communicate with Agent. Status code: {agent_response.status_code}"
                }
                return

            response_text = agent_response.json()['text']
            print(f"Background task {task_id} got response: {response_text[:100]}..." if len(response_text) > 100 else f"Background task {task_id} got response: {response_text}")
            background_tasks[task_id] = {
                "status": "completed",
                "result": response_text,
                "error": None
            }
            print(f"Background task {task_id} marked as completed")
            
    except httpx.TimeoutException:
        background_tasks[task_id] = {
            "status": "failed",
            "result": None,
            "error": "Request timed out. The agent is taking longer than expected to respond."
        }
    except httpx.ConnectError:
        background_tasks[task_id] = {
            "status": "failed",
            "result": None,
            "error": "Failed to connect to the agent. Please check if the agent service is running."
        }
    except Exception as e:
        print(f"Error in background task {task_id}: {e}")
        background_tasks[task_id] = {
            "status": "failed",
            "result": None,
            "error": f"An error occurred while communicating with the agent: {str(e)}"
        }

async def chat(message, history, agent_mode, request: gr.Request):
    username = request.username
    token = request.request.session["access_token"]
    print(f"username={username}, message={message}, agent_mode={agent_mode}")

    try:
        # Start background task - use internal call instead of HTTP
        task_id = str(uuid.uuid4())
        
        # Store task info
        background_tasks[task_id] = {
            "status": "processing",
            "result": None,
            "error": None
        }
        
        # Start background task directly
        task_data = {
            "message": message,
            "agent_mode": agent_mode,
            "token": token,
            "username": username
        }
        asyncio.create_task(process_chat_background(task_id, task_data))
        
        print(f"Started background task {task_id} for user {username}")
        
        # Poll for completion every 5 seconds (faster for better UX)
        max_polls = 120  # 10 minutes max (5 sec intervals)
        for i in range(max_polls):
            await asyncio.sleep(5)
            
            # Check task status directly from memory
            if task_id not in background_tasks:
                return "Task not found. Please try again."
                
            task_status = background_tasks[task_id]
            
            if task_status["status"] == "completed":
                print(f"Task {task_id} completed after {(i+1)*5} seconds")
                result = task_status["result"]
                # Clean up completed task
                del background_tasks[task_id]
                return result
            elif task_status["status"] == "failed":
                print(f"Task {task_id} failed after {(i+1)*5} seconds")
                error = task_status["error"]
                # Clean up failed task
                del background_tasks[task_id]
                return f"❌ Error: {error}"
            
            # Show progress in logs every 30 seconds (every 6 polls)
            if (i + 1) % 6 == 0:
                elapsed_minutes = ((i + 1) * 5) // 60
                elapsed_seconds = ((i + 1) * 5) % 60
                print(f"Task {task_id} still processing... ({elapsed_minutes}m {elapsed_seconds}s elapsed)")
        
        # Clean up timed out task
        if task_id in background_tasks:
            del background_tasks[task_id]
        return "⏰ Request timed out after 10 minutes. Please try again with a simpler question."
        
    except Exception as e:
        print(f"Error in chat polling: {e}")
        return f"❌ An error occurred while processing your request: {str(e)}"

def on_gradio_app_load(request: gr.Request):
    # if request.username not present set username
    if not request.username:
        request.username = "Alice"
    return f"Logout ({request.username})", [gr.ChatMessage(
        role="assistant",
        content=f"Hi {request.username}, I'm your friendly corporate agent. Tell me how I can help. "
    )], "Single Agent(Weather)"  # Default to Single Agent(Weather) mode

def logout_click(request: gr.Request):
    print(f"logout function")
    #request.session.clear()
    return f"Logout ({request.username})", [], "Single Agent(Weather)"

with gr.Blocks() as gradio_app:
    header = gr.Markdown("Welcome to the Agent")

    # Agent mode selector
    agent_mode = gr.Radio(
        choices=["Single Agent(Weather)", "Multi-Agent(Travel)"],
        value="Single Agent(Weather)",
        label="Agent Mode",
        info="Choose between Single Agent or Multi-Agent mode"
    )

    chat = gr.ChatInterface(
        fn=chat,
        type="messages",
        additional_inputs=[agent_mode],
        chatbot=gr.Chatbot(
            type="messages",
            label="Book your next business trip with ease",
            avatar_images=(user_avatar, bot_avatar)
        )
    )

    logout_button = gr.Button(value="Logout", variant="secondary")
    logout_button.click(
        fn=None,
        js=f"() => {{ console.log('Logout Button clicked!'); console.log('Redirecting to: {LOGOUT_URL}'); window.location.href='{LOGOUT_URL}'; }}"
    )

#        js=f"() => {{ console.log('Logout Button clicked!'); console.log('Redirecting to: {LOGOUT_URL}'); window.location.href='{LOGOUT_URL}'; }}"

    gradio_app.load(on_gradio_app_load, inputs=None, outputs=[logout_button, chat.chatbot, agent_mode])

gr.mount_gradio_app(fastapi_app, gradio_app, path=CHAT_PATH, auth_dependency=check_auth)

def main():
    uvicorn.run(
        fastapi_app,
        host=os.getenv("FASTAPI_HOST", "0.0.0.0"),
        port=int(os.getenv("FASTAPI_PORT", "8000")),
        timeout_graceful_shutdown=300,
        timeout_keep_alive=300
    )

if __name__ == "__main__":
    main()
