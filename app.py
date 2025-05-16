from flask import Flask, request, jsonify, render_template, redirect, url_for
from models import db, User
import os

app = Flask(__name__)

# Ensure the database is saved in a directory that Render can access
# For Render deployment, SQLite might not persist well, so PostgreSQL is recommended in production.

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///mydb.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db.init_app(app)

# Create DB Tables
@app.before_first_request
def create_tables():
    with app.app_context():
        db.create_all()

# Home with form UI
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

# Handle form submission (from UI)
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    
    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return "User already exists!", 400  # Can customize this as needed
    
    user = User(name=name, email=email)
    try:
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}", 500

# POST API (JSON)
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Missing name or email"}), 400
    
    # Check if email already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "User already exists!"}), 400
    
    new_user = User(name=data['name'], email=data['email'])
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# GET API
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

if __name__ == '__main__':
    # Get the PORT environment variable provided by Render or default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)  # Run the app on 0.0.0.0 to be accessible externally
