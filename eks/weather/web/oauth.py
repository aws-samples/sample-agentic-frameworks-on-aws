from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
import os

def add_oauth_routes(fastapi_app: FastAPI):
    OAUTH_SIGNIN_URL = os.getenv("OAUTH_SIGNIN_URL")
    OAUTH_LOGOUT_URL = os.getenv("OAUTH_LOGOUT_URL")
    OAUTH_WELL_KNOWN_ENDPOINT_URL = os.getenv("OAUTH_WELL_KNOWN_URL")
    OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
    OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
    OAUTH_CALLBACK_URI = "http://localhost:8000/callback"
    REDIRECT_AFTER_LOGOUT_URL = "http://localhost:8000/chat"

    oauth = OAuth()
    oauth.register(
        name="oauth_provider",
        client_id=OAUTH_CLIENT_ID,
        client_secret=OAUTH_CLIENT_SECRET,
        client_kwargs={"scope": "openid email profile"},
        server_metadata_url=OAUTH_WELL_KNOWN_ENDPOINT_URL,
        redirect_uri=OAUTH_CALLBACK_URI,
    )

    @fastapi_app.get("/login")
    async def login(req: Request):
        return await oauth.oauth_provider.authorize_redirect(req, OAUTH_CALLBACK_URI)

    @fastapi_app.get("/callback")
    async def callback(req: Request):
        tokens = await oauth.oauth_provider.authorize_access_token(req)
        print(tokens)
        access_token = tokens["access_token"]
        # Try to get username from different possible fields (generic OAuth approach)
        username = tokens["userinfo"].get("username") or tokens["userinfo"].get("cognito:username") or tokens["userinfo"].get("preferred_username") or tokens["userinfo"].get("sub")
        req.session["access_token"] = access_token
        req.session["username"] = username
        print(f"username={username} access_token={access_token}")
        return RedirectResponse(url="/chat")

    @fastapi_app.get("/logout")
    async def logout(req: Request):
        req.session.clear()
        logout_url = f"{OAUTH_LOGOUT_URL}&logout_uri={REDIRECT_AFTER_LOGOUT_URL}"
        return RedirectResponse(url=logout_url)
