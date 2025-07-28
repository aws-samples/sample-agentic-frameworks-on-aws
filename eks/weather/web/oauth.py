from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
import os
import pprint

def add_oauth_routes(
    fastapi_app: FastAPI,
    OAUTH_CALLBACK_URI: str,
    UI_URL: str,
):
    OAUTH_SIGNIN_URL = os.getenv("OAUTH_SIGNIN_URL")
    OAUTH_LOGOUT_URL = os.getenv("OAUTH_LOGOUT_URL")
    OAUTH_WELL_KNOWN_ENDPOINT_URL = os.getenv("OAUTH_WELL_KNOWN_URL")
    OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
    OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")

    # Print environment variables and derived URLs
    print(f"OAUTH_SIGNIN_URL:{OAUTH_SIGNIN_URL}")
    print(f"OAUTH_LOGOUT_URL:{OAUTH_LOGOUT_URL}") 
    print(f"OAUTH_WELL_KNOWN_ENDPOINT_URL:{OAUTH_WELL_KNOWN_ENDPOINT_URL}")
    print(f"OAUTH_CLIENT_ID:{OAUTH_CLIENT_ID}")
    print(f"OAUTH_CLIENT_SECRET:{OAUTH_CLIENT_SECRET}")
 


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
        print("handling /login")
        print(f"returning redirect with OAUTH_CALLBACK_URI={OAUTH_CALLBACK_URI}")
        #pprint.pprint(vars(req))
        return await oauth.oauth_provider.authorize_redirect(req, OAUTH_CALLBACK_URI)

    @fastapi_app.get("/callback")
    async def callback(req: Request):
        print("handling /callback")
        tokens = await oauth.oauth_provider.authorize_access_token(req)
        print(tokens)
        access_token = tokens["access_token"]
        # Try to get username from different possible fields (generic OAuth approach)
        username = tokens["userinfo"].get("username") or tokens["userinfo"].get("cognito:username") or tokens["userinfo"].get("preferred_username") or tokens["userinfo"].get("sub")
        req.session["access_token"] = access_token
        req.session["username"] = username
        print(f"username={username} access_token={access_token}")
        return RedirectResponse(url=UI_URL)

    @fastapi_app.get("/logout")
    async def logout(req: Request):
        print("handling /logout")
        req.session.clear()
        # Construct proper Cognito logout URL with required parameters
        logout_url = f"{OAUTH_LOGOUT_URL}&logout_uri={UI_URL}"
        print(f"Redirecting to {logout_url}")
        return RedirectResponse(url=logout_url)
