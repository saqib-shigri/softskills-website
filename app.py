from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import json

app = Flask(__name__)
app.secret_key = "my-secret-key-12345"

# ============================================
# SUPABASE CONFIGURATION - APNI VALUES DALO
# ============================================
SUPABASE_URL = "https://xnytuacpjrlagnxktjgd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhueXR1YWNwanJsYWdueGt0amdkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc3MTc3NTcsImV4cCI6MjA5MzI5Mzc1N30.x5qxaiBcYu_s0wIMMQGx08Ws0akyOGeltYoyaRwg1C8"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ============================================
# DATABASE FUNCTIONS
# ============================================

def get_data(table):
    """Get all data from a table"""
    try:
        # URL mein bhi apikey parameter add karo
        url = f"{SUPABASE_URL}/rest/v1/{table}?select=*&apikey={SUPABASE_KEY}"
        response = requests.get(url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        })
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Exception: {e}")
        return []

def insert_data(table, data):
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}?apikey={SUPABASE_KEY}"
        response = requests.post(url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }, json=data)
        return response.status_code in [200, 201]
    except:
        return False

def update_data(table, id, data):
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{id}&apikey={SUPABASE_KEY}"
        response = requests.patch(url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }, json=data)
        return response.status_code in [200, 204]
    except:
        return False

def delete_data(table, id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{id}&apikey={SUPABASE_KEY}"
        response = requests.delete(url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        })
        return response.status_code in [200, 204]
    except:
        return False

# ============================================
# SIMPLE ADMIN SESSION
# ============================================
admin_logged_in = False

# ============================================
# MAIN WEBSITE ROUTES
# ============================================

@app.route('/')
def index():
    # Get data from database
    services = get_data('services')
    projects = get_data('projects')
    courses = get_data('courses')
    jobs = get_data('jobs')
    
    # Filter only visible items
    services = [s for s in services if s.get('is_visible', True)]
    projects = [p for p in projects if p.get('is_visible', True)]
    courses = [c for c in courses if c.get('is_visible', True)]
    jobs = [j for j in jobs if j.get('is_active', True)]
    
    return render_template('index.html', 
                         services=services, 
                         projects=projects,
                         courses=courses,
                         jobs=jobs)

# ============================================
# ADMIN LOGIN ROUTES
# ============================================

@app.route('/secret-admin/login', methods=['GET', 'POST'])
def admin_login():
    global admin_logged_in
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == "admin" and password == "admin123":
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
    services_count = len(get_data('services'))
    projects_count = len(get_data('projects'))
    courses_count = len(get_data('courses'))
    jobs_count = len(get_data('jobs'))
    
    return render_template('admin/dashboard.html',
                         services_count=services_count,
                         projects_count=projects_count,
                         courses_count=courses_count,
                         jobs_count=jobs_count)

# ============================================
# SERVICES CRUD
# ============================================

@app.route('/secret-admin/services')
@login_required
def admin_services():
    services = get_data('services')
    return render_template('admin/services.html', services=services)

@app.route('/secret-admin/services/add', methods=['GET', 'POST'])
@login_required
def admin_add_service():
    if request.method == 'POST':
        features = request.form.get('features', '').split('\n')
        features = [f.strip() for f in features if f.strip()]
        
        data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'icon': request.form.get('icon', 'fa-cogs'),
            'features': features,
            'is_visible': request.form.get('is_visible') == 'on',
            'display_order': int(request.form.get('display_order', 0))
        }
        if insert_data('services', data):
            flash('Service added successfully!', 'success')
        else:
            flash('Error adding service', 'error')
        return redirect(url_for('admin_services'))
    
    return render_template('admin/service_form.html', action='Add')

@app.route('/secret-admin/services/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_service(id):
    if request.method == 'POST':
        features = request.form.get('features', '').split('\n')
        features = [f.strip() for f in features if f.strip()]
        
        data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'icon': request.form.get('icon', 'fa-cogs'),
            'features': features,
            'is_visible': request.form.get('is_visible') == 'on',
            'display_order': int(request.form.get('display_order', 0))
        }
        if update_data('services', id, data):
            flash('Service updated successfully!', 'success')
        else:
            flash('Error updating service', 'error')
        return redirect(url_for('admin_services'))
    
    services = get_data('services')
    service = next((s for s in services if s['id'] == id), None)
    return render_template('admin/service_form.html', action='Edit', service=service)

@app.route('/secret-admin/services/delete/<int:id>')
@login_required
def admin_delete_service(id):
    if delete_data('services', id):
        flash('Service deleted successfully!', 'success')
    else:
        flash('Error deleting service', 'error')
    return redirect(url_for('admin_services'))

# ============================================
# PROJECTS CRUD
# ============================================

@app.route('/secret-admin/projects')
@login_required
def admin_projects():
    projects = get_data('projects')
    return render_template('admin/projects.html', projects=projects)

@app.route('/secret-admin/projects/add', methods=['GET', 'POST'])
@login_required
def admin_add_project():
    if request.method == 'POST':
        data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'icon': request.form.get('icon', 'fa-globe'),
            'image_url': request.form.get('image_url'),
            'demo_link': request.form.get('demo_link'),
            'category': request.form.get('category', 'website'),
            'is_visible': request.form.get('is_visible') == 'on',
            'display_order': int(request.form.get('display_order', 0))
        }
        if insert_data('projects', data):
            flash('Project added successfully!', 'success')
        else:
            flash('Error adding project', 'error')
        return redirect(url_for('admin_projects'))
    
    return render_template('admin/project_form.html', action='Add')

@app.route('/secret-admin/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_project(id):
    if request.method == 'POST':
        data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'icon': request.form.get('icon', 'fa-globe'),
            'image_url': request.form.get('image_url'),
            'demo_link': request.form.get('demo_link'),
            'category': request.form.get('category', 'website'),
            'is_visible': request.form.get('is_visible') == 'on',
            'display_order': int(request.form.get('display_order', 0))
        }
        if update_data('projects', id, data):
            flash('Project updated successfully!', 'success')
        else:
            flash('Error updating project', 'error')
        return redirect(url_for('admin_projects'))
    
    projects = get_data('projects')
    project = next((p for p in projects if p['id'] == id), None)
    return render_template('admin/project_form.html', action='Edit', project=project)

@app.route('/secret-admin/projects/delete/<int:id>')
@login_required
def admin_delete_project(id):
    if delete_data('projects', id):
        flash('Project deleted successfully!', 'success')
    else:
        flash('Error deleting project', 'error')
    return redirect(url_for('admin_projects'))

# ============================================
# COURSES CRUD
# ============================================

@app.route('/secret-admin/courses')
@login_required
def admin_courses():
    courses = get_data('courses')
    return render_template('admin/courses.html', courses=courses)

@app.route('/secret-admin/courses/add', methods=['GET', 'POST'])
@login_required
def admin_add_course():
    if request.method == 'POST':
        features = request.form.get('features', '').split('\n')
        features = [f.strip() for f in features if f.strip()]
        
        data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'icon': request.form.get('icon', 'fa-graduation-cap'),
            'features': features,
            'price': request.form.get('price'),
            'duration': request.form.get('duration'),
            'is_visible': request.form.get('is_visible') == 'on',
            'display_order': int(request.form.get('display_order', 0))
        }
        if insert_data('courses', data):
            flash('Course added successfully!', 'success')
        else:
            flash('Error adding course', 'error')
        return redirect(url_for('admin_courses'))
    
    return render_template('admin/course_form.html', action='Add')

@app.route('/secret-admin/courses/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_course(id):
    if request.method == 'POST':
        features = request.form.get('features', '').split('\n')
        features = [f.strip() for f in features if f.strip()]
        
        data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'icon': request.form.get('icon', 'fa-graduation-cap'),
            'features': features,
            'price': request.form.get('price'),
            'duration': request.form.get('duration'),
            'is_visible': request.form.get('is_visible') == 'on',
            'display_order': int(request.form.get('display_order', 0))
        }
        if update_data('courses', id, data):
            flash('Course updated successfully!', 'success')
        else:
            flash('Error updating course', 'error')
        return redirect(url_for('admin_courses'))
    
    courses = get_data('courses')
    course = next((c for c in courses if c['id'] == id), None)
    return render_template('admin/course_form.html', action='Edit', course=course)

@app.route('/secret-admin/courses/delete/<int:id>')
@login_required
def admin_delete_course(id):
    if delete_data('courses', id):
        flash('Course deleted successfully!', 'success')
    else:
        flash('Error deleting course', 'error')
    return redirect(url_for('admin_courses'))

# ============================================
# JOBS CRUD
# ============================================

@app.route('/secret-admin/jobs')
@login_required
def admin_jobs():
    jobs = get_data('jobs')
    return render_template('admin/jobs.html', jobs=jobs)

@app.route('/secret-admin/jobs/add', methods=['GET', 'POST'])
@login_required
def admin_add_job():
    if request.method == 'POST':
        requirements = request.form.get('requirements', '').split('\n')
        requirements = [r.strip() for r in requirements if r.strip()]
        
        data = {
            'title': request.form.get('title'),
            'location': request.form.get('location'),
            'job_type': request.form.get('job_type'),
            'description': request.form.get('description'),
            'requirements': requirements,
            'is_active': request.form.get('is_active') == 'on',
            'display_order': int(request.form.get('display_order', 0))
        }
        if insert_data('jobs', data):
            flash('Job added successfully!', 'success')
        else:
            flash('Error adding job', 'error')
        return redirect(url_for('admin_jobs'))
    
    return render_template('admin/job_form.html', action='Add')

@app.route('/secret-admin/jobs/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_job(id):
    if request.method == 'POST':
        requirements = request.form.get('requirements', '').split('\n')
        requirements = [r.strip() for r in requirements if r.strip()]
        
        data = {
            'title': request.form.get('title'),
            'location': request.form.get('location'),
            'job_type': request.form.get('job_type'),
            'description': request.form.get('description'),
            'requirements': requirements,
            'is_active': request.form.get('is_active') == 'on',
            'display_order': int(request.form.get('display_order', 0))
        }
        if update_data('jobs', id, data):
            flash('Job updated successfully!', 'success')
        else:
            flash('Error updating job', 'error')
        return redirect(url_for('admin_jobs'))
    
    jobs = get_data('jobs')
    job = next((j for j in jobs if j['id'] == id), None)
    return render_template('admin/job_form.html', action='Edit', job=job)

@app.route('/secret-admin/jobs/delete/<int:id>')
@login_required
def admin_delete_job(id):
    if delete_data('jobs', id):
        flash('Job deleted successfully!', 'success')
    else:
        flash('Error deleting job', 'error')
    return redirect(url_for('admin_jobs'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)