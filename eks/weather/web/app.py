import os
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
import uvicorn
import gradio as gr
import httpx
import oauth

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

def chat(message, history, agent_mode, request: gr.Request):
    username = request.username
    token = request.request.session["access_token"]
    print(f"username={username}, message={message}, agent_mode={agent_mode}")

    # Select endpoint based on agent mode
    if agent_mode == "Single Agent(Weather)":
        endpoint_url = AGENT_UI_ENDPOINT_URL_1
        print(f"Using Single Agent(Weather) endpoint: {endpoint_url}")
    else:  # Multi-Agent(Travel)
        endpoint_url = AGENT_UI_ENDPOINT_URL_2
        print(f"Using Multi-Agent(Travel) endpoint: {endpoint_url}")

    agent_response = httpx.post(
        endpoint_url,
        headers={"Authorization": f"Bearer {token}"},
        json={"text": message},
        timeout=30,
    )

    if agent_response.status_code == 401 or agent_response.status_code ==403:
        return f"Agent returned authorization error. Try to re-login. Status code: {agent_response.status_code}"

    if agent_response.status_code != 200:
        return f"Failed to communicate with Agent. Status code: {agent_response.status_code}"

    response_text = agent_response.json()['text']
    return response_text

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
        timeout_graceful_shutdown=1,
    )

if __name__ == "__main__":
    main()
