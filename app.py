from flask import Flask, render_template, request, redirect, url_for, session
import os
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Temporary in-memory database mock
USER_DB = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth', methods=['POST'])
def auth():
    action = request.args.get('action', 'login')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if action == 'signup':
        if email in USER_DB:
            return "<h1>Account already exists! Go back and login.</h1>", 400
        USER_DB[email] = password
        session['user'] = email
        return redirect(url_for('dashboard'))
        
    elif action == 'login':
        if email in USER_DB and USER_DB[email] == password:
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            return "<h1>Invalid email or password!</h1>", 401

    return redirect(url_for('index'))

@app.route('/login/google')
def login_google():
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
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
    code = request.args.get("code")
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": request.url_root.replace('http://', 'https://') + "callback",
        "grant_type": "authorization_code"
    }
    token_response = requests.post(token_endpoint, data=token_data).json()
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return """
    <div style="display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #E0E7FF 0%, #F3E8FF 100%); margin: 0;">
        <h1 style="font-size: 2.5rem; color: #1F2937; text-align: center; padding: 0 20px;">Welcome to your Application!<br><span style="color: #10B981;">Authentication Successful.</span></h1>
    </div>
    """

if __name__ == '__main__':
    app.run(debug=True)