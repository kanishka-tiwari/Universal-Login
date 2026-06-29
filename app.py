from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Mock database tracking credentials and active device session tokens
USER_DB = {}          # format: {email: password}
ACTIVE_SESSIONS = {}  # format: {email: session_id}

def validate_password(password):
    """Enforces standard registration criteria: 8+ chars, 1 number, 1 uppercase."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number."
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter."
    return None

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/auth', methods=['POST'])
def auth():
    action = request.args.get('action', 'login')
    email = request.form.get('email').strip().lower()
    password = request.form.get('password')
    
    if action == 'signup':
        if email in USER_DB:
            return "<h1>Account already exists! Go back and login.</h1>", 400
        
        # password validation gate check
        password_error = validate_password(password)
        if password_error:
            return f"<h1>Registration Failed</h1><p>{password_error}</p><a href='/'>Go Back</a>", 400
            
        USER_DB[email] = password
        
        # create user session variables
        session['user'] = email
        current_session_token = os.urandom(16).hex()
        session['session_token'] = current_session_token
        ACTIVE_SESSIONS[email] = current_session_token
        return redirect(url_for('dashboard'))
        
    elif action == 'login':
        if email in USER_DB and USER_DB[email] == password:
            # multi-device session manager validation logic override
            current_session_token = os.urandom(16).hex()
            session['user'] = email
            session['session_token'] = current_session_token
            ACTIVE_SESSIONS[email] = current_session_token
            return redirect(url_for('dashboard'))
        else:
            return "<h1>Invalid email or password!</h1>", 401

    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email').strip().lower()
    if email in USER_DB:
        return jsonify({"message": f"Success! A verification reset sequence has been initiated for {email}."}), 200
    return jsonify({"error": "This email address is not registered in our system."}), 404

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
    
    # Mock account creation or mapping logic step for social logins
    email = token_response.get("email", "google_user@example.com")
    current_session_token = os.urandom(16).hex()
    session['user'] = email
    session['session_token'] = current_session_token
    ACTIVE_SESSIONS[email] = current_session_token
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    # Route Protection Check: Block direct URL hits if unauthenticated
    if 'user' not in session:
        return redirect(url_for('index'))
        
    # Active concurrent device confirmation session token verification check
    user = session['user']
    if ACTIVE_SESSIONS.get(user) != session.get('session_token'):
        session.clear()
        return "<h1>Session expired. Logged in from another device.</h1><a href='/'>Login Again</a>", 401

    return """
    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #E0E7FF 0%, #F3E8FF 100%); margin: 0;">
        <h1 style="font-size: 2.5rem; color: #1F2937; text-align: center; padding: 0 20px;">Welcome to your Application!<br><span style="color: #10B981;">Authentication Successful.</span></h1>
        <a href="/logout" style="margin-top: 20px; padding: 10px 20px; background-color: #F43F5E; color: white; text-decoration: none; font-weight: bold; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">Logout</a>
    </div>
    """

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)