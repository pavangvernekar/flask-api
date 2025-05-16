from flask import Flask, request, jsonify, render_template, redirect, url_for
from models import db, User
import os

app = Flask(__name__, instance_relative_config=True)

# Ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Path to the SQLite database in the instance folder
db_path = 'C:/Users/Lenovo/Desktop/flask_api_project/instance/mydb.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db.init_app(app)

# Create tables if not exist
with app.app_context():
    db.create_all()

# UI: Home page with form
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

# UI: Form submission
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']

    if User.query.filter_by(email=email).first():
        return "User already exists!", 400

    user = User(name=name, email=email)
    try:
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}", 500

# API: Create user via JSON
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Missing name or email"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "User already exists!"}), 400

    new_user = User(name=data['name'], email=data['email'])
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# API: Get all users
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
