from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'my-secret-key-12345')

# ============================================
# SUPABASE CONFIGURATION
# ============================================
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ============================================
# DATABASE FUNCTIONS
# ============================================

def get_data(table):
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def insert_data(table, data):
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}"
        response = requests.post(url, headers=headers, json=data)
        return response.status_code in [200, 201]
    except:
        return False

# ============================================
# SIMPLE ADMIN SESSION (No Database)
# ============================================
admin_logged_in = False

@app.route('/')
def index():
    return render_template('index.html')

# ============================================
# ADMIN LOGIN
# ============================================
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

@app.route('/secret-admin/login', methods=['GET', 'POST'])
def admin_login():
    global admin_logged_in
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == "admin" and password == ADMIN_PASSWORD:
            admin_logged_in = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Wrong username or password", "error")
    
    return render_template('admin/login.html')

@app.route('/secret-admin/logout')
def admin_logout():
    global admin_logged_in
    admin_logged_in = False
    return redirect(url_for('admin_login'))

def login_required(f):
    def wrapper(*args, **kwargs):
        global admin_logged_in
        if not admin_logged_in:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# ============================================
# ADMIN DASHBOARD
# ============================================

@app.route('/secret-admin/')
@login_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/secret-admin/jobs')
@login_required
def admin_jobs():
    return render_template('admin/jobs.html')

# Simple route for testing
@app.route('/health')
def health():
    return "OK", 200

# ============================================
# RUN APP - Railway Compatible
# ============================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)