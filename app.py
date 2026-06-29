from flask import Flask, render_template, request, redirect, url_for, session
import os
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required to use sessions for authentication tracking

# Google OAuth Configuration from Render environment variables
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth', methods=['POST'])
def auth():
    action = request.args.get('action', 'login')
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Simple placeholder routing validation for Email/Password Sign Up/In
    return redirect(url_for('dashboard'))

@app.route('/login/google')
def login_google():
    # Get Google's authorization endpoint
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Construct the request URI for Google Login
    request_uri = (
        f"{authorization_endpoint}?"
        f"response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={request.url_root.replace('http://', 'https://')}callback"
        f"&scope=openid%20email%20profile"
    )
    return redirect(request_uri)

@app.route('/callback')
def callback():
    # Get the authorization code sent back back by Google
    code = request.args.get("code")
    
    # Find endpoints to look up token information
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare credentials data to exchange the authorization code for an access token
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": request.url_root.replace('http://', 'https://')}callback,
        "grant_type": "authorization_code"
    }

    # Send POST request to fetch token authentication data
    token_response = requests.post(token_endpoint, data=token_data).json()
    
    # User is now authenticated
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return "<h1>Welcome to your Application! Authentication Successful.</h1>"

if __name__ == '__main__':
    app.run(debug=True)