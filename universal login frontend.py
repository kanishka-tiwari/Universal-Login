# app.py
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth', methods=['POST'])
def auth():
    action = request.args.get('action', 'login')
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Handle direct email/password routing validation here if bypassing client-side SDK
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return "<h1>Welcome to your Application! Authentication Successful.</h1>"

if __name__ == '__main__':
    app.run(debug=True) 