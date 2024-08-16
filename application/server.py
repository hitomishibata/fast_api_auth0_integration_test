import requests
import http.client
import json
from os import environ as env
from dotenv import find_dotenv, load_dotenv
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, render_template, session, url_for

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration"
)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True),
        audience=env.get("AUDIENCE")
    )

@app.route("/callback", methods=["GET","POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
               "returnTo": url_for("home", _external=True),
               "client_id": env.get("AUTH0_CLIENT_ID"), 
            },
            quote_via=quote_plus,
        )
    )

@app.route("/")
def home():
    return render_template("home.html", session=session.get('user'), prety=json.dumps(session.get('user'), indent=4))

@app.route("/api")
def connect_to_api():
    access_token=requests.session.get("user").get("access_token")
    url=f"{env.get("API_URL")}/api/messages/protected"
    if access_token is None:
        headers = {}
    else:
        headers ={
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}"
            }
    res = requests.get(url, headers=headers)
    return res.json() 
