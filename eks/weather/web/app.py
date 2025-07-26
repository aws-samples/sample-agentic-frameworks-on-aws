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
print(f"AGENT_UI_ENDPOINT_URL_1={AGENT_UI_ENDPOINT_URL_1}")
print(f"AGENT_UI_ENDPOINT_URL_2={AGENT_UI_ENDPOINT_URL_2}")
user_avatar = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
bot_avatar = "https://cdn-icons-png.flaticon.com/512/4712/4712042.png"

fastapi_app = FastAPI()
fastapi_app.add_middleware(SessionMiddleware, secret_key="secret")
oauth.add_oauth_routes(fastapi_app)

@fastapi_app.get("/")
async def root():
    print("🏠 Root endpoint accessed")
    return RedirectResponse(url="./chat/")

def check_auth(req: Request):
    if not "access_token" in req.session or not "username" in req.session:
        print("check_auth::not found, redirecting to /login")
        raise HTTPException(status_code=302, detail="Redirecting to login", headers={"Location": "/login"})

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
        js="() => window.location.href='/logout'"
    )

    gradio_app.load(on_gradio_app_load, inputs=None, outputs=[logout_button, chat.chatbot, agent_mode])

gr.mount_gradio_app(fastapi_app, gradio_app, path="/chat", auth_dependency=check_auth)

def main():
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", "8000"))
    uvicorn.run(fastapi_app, host=host, port=port)

if __name__ == "__main__":
    main()
