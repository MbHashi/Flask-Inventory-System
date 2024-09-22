from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from bson.objectid import ObjectId  # Import ObjectId from bson
import logging
from datetime import datetime
from db import mongo  # Import from the new db.py to avoid circular imports

app = Flask(__name__)

# Configuration
app.config.from_object('config.Config')

# Initialize MongoDB
mongo.init_app(app)

# Setting up authentication (Flask-login)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Inventory Collection
inventory_collection = mongo.db.inventory

from models import User  # Delayed import

# Setting up basic logging
logging.basicConfig(level=logging.DEBUG)

@app.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.path} {request.form}")
    logging.info(f"Headers: {request.headers}")

@app.after_request
def log_response_info(response):
    logging.info(f"Response status: {response.status}")
    return response


# Creating a User
@app.route('/register', methods=['GET', 'POST'])
def register():
    from models import User  # Ensure that the User model is imported
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        logging.debug(f"Registration attempt for username: {username}")

        # Check if the username already exists
        existing_user = User.find_by_username(username)
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        # Create new user
        new_user = User.create_user(mongo, username, password)
        login_user(new_user)
        flash('Registration successful! You are now logged in.', 'success')
        return redirect(url_for('home'))
    
    return render_template('register.html')

# Finding a User
@login_manager.user_loader
def load_user(user_id):
    from models import User  # Ensure that the User model is imported
    # Fetch the user document from MongoDB by ObjectId
    try:
        user_id = ObjectId(user_id)
    except Exception as e:
        logging.error(f"Invalid user_id: {user_id}. Error: {e}")
        return None
    user_data = mongo.db.users.find_one({"_id": user_id})
    if user_data:
        return User(user_data['username'], user_data['password_hash'], user_data['_id'])
    return None

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    from models import User  # Ensure that the User model is imported
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user by username
        user = User.find_by_username(username)
        
        if user:
            # Check if the password matches
            if user.check_password(password):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                # Incorrect password
                flash('Incorrect password. Please try again.', 'password_error')
        else:
            # User not found
            flash('User not found. Please check your username.', 'username_error')
            
    return render_template('login.html')


# User logout route
@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login')) # Redirecting to the Login page after log out

# Home/ landing page after authentication
@app.route('/home')
@login_required
def home():
    try:
        page = request.args.get('page', 1, type=int)  # Current page number
        per_page = 10  # Items per page

        # Pulls all inventory items from MongoDB with pagination
        total_items = inventory_collection.count_documents({})
        items = inventory_collection.find().skip((page - 1) * per_page).limit(per_page)

        # Calculate total pages
        total_pages = (total_items + per_page - 1) // per_page  # To round up

        return render_template('inventory.html', 
                               items=items, 
                               total_items=total_items, 
                               page=page, 
                               per_page=per_page,
                               total_pages=total_pages)
    except Exception as e:
        logging.error(f"Error loading home page: {str(e)}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('login'))

# Inventory route
@app.route('/inventory', methods=['GET'])
@login_required
def inventory():
    # Fetch all inventory items from the MongoDB collection
    try:
        # Pagination setup (if you want to paginate the inventory items)
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Define how many items you want per page
        
        # Fetch total number of items and paginated items
        total_items = inventory_collection.count_documents({})
        items = inventory_collection.find().skip((page - 1) * per_page).limit(per_page)
        
        # Calculate total pages
        total_pages = (total_items + per_page - 1) // per_page  # To round up
        
        return render_template('inventory.html', 
                               items=items, 
                               total_items=total_items, 
                               page=page, 
                               per_page=per_page,
                               total_pages=total_pages)
    
    except Exception as e:
        flash(f'An error occurred while fetching inventory: {str(e)}', 'error')
        return redirect(url_for('home'))
    
# # Test to add a new item via MongoDB
# @app.route('/add_item', methods=['POST'])
# @login_required
# def add_item():
#     if request.method == 'POST':
#         try:
#             item_name = request.form['name']
#             quantity = request.form['quantity']
#             price = request.form['price']
#             description = request.form['description']

#             # Validation to ensure all fields are filled prior to submitting
#             if not all([item_name, quantity, price, description]):
#                     flash('All fields are required!', 'error')
#                     return redirect('/')

#             # Inserting item into MongoDB with a timestamp
#             inventory_collection.insert_one({
#                 'name': item_name,
#                 'quantity': int(quantity),
#                 'price': float(price),
#                 'description': description,
#                 'created_at': datetime.utcnow()  # Add creation timestamp
#             })

#             flash('Item added successfully!', 'success')
#             return redirect('/')
#         except Exception as e:
#             flash(f'Error adding item: {str(e)}', 'error')
#             return redirect('/')
        
#     return render_template("add_item.html")

# Adding items to the DB with print statements
@app.route('/add_item', methods=['POST'])
@login_required
def add_item():
    from models import User  # Ensure that the User model is imported
    if request.method == 'POST':
        item_name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']
        description = request.form['description']

        # Server-side validation
        if not all([item_name, quantity, price, description]):
            flash('All fields are required!', 'error')
            return redirect(url_for('home'))

        try:
            # Insert item into MongoDB
            inventory_collection.insert_one({
                'name': item_name,
                'quantity': int(quantity),
                'price': float(price),
                'description': description,
                'created_at': datetime.utcnow()
            })

            flash('Item added successfully!', 'success')
            return redirect(url_for('home'))

        except Exception as e:
            flash(f'Error adding item: {str(e)}', 'error')
            return redirect(url_for('home'))
        
# Route to delete an item
@app.route('/delete_item/<item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    try:
        # Delete the item by its ObjectId from MongoDB
        result = inventory_collection.delete_one({"_id": ObjectId(item_id)})
        
        if result.deleted_count > 0:
            flash('Item deleted successfully!', 'success')
        else:
            flash('Item not found!', 'error')

    except Exception as e:
        flash(f'Error deleting item: {str(e)}', 'error')

    return redirect('/')

# Route to show the update form
@app.route('/update_item/<item_id>', methods=['GET'])
@login_required
def update_item_form(item_id):
    try:
        # Fetch the item to be updated
        item = inventory_collection.find_one({"_id": ObjectId(item_id)})
        if item:
            return render_template('update_item.html', item=item)
        else:
            flash('Item not found!', 'error')
            return redirect('/')
    except Exception as e:
        flash(f'Error fetching item: {str(e)}', 'error')
        return redirect('/')

# Route to handle the item update
@app.route('/update_item/<item_id>', methods=['POST'])
@login_required
def update_item(item_id):
    try:
        item_name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']
        description = request.form['description']

        # Validation to ensure all fields are filled before submitting
        if not all([item_name, quantity, price, description]):
            flash('All fields are required!', 'error')
            return redirect(url_for('update_item_form', item_id=item_id))

        # Update the item in MongoDB
        result = inventory_collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": {
                "name": item_name,
                "quantity": int(quantity),
                "price": float(price),
                "description": description,
                "updated_at": datetime.utcnow()  # Add update timestamp
            }}
        )

        if result.modified_count > 0:
            flash('Item updated successfully!', 'success')
        else:
            flash('No changes were made to the item.', 'info')

    except Exception as e:
        flash(f'Error updating item: {str(e)}', 'error')

    return redirect('/')

# Search feature:
@app.route('/search', methods=['GET'])
@login_required
def search_items():
    query = request.args.get('q')  # Get search query from URL
    search_results = []
    
    if query:
        search_results = inventory_collection.find({
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
        })
    
    return render_template('search_results.html', items=search_results, query=query)

# Pagination:
@app.route('/paginated_home')
@login_required
def paginated_home():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Items per page
    
    total_items = inventory_collection.count_documents({})
    items = inventory_collection.find().skip((page - 1) * per_page).limit(per_page)
    
    return render_template('index.html', items=items, page=page, total_items=total_items, per_page=per_page)


@app.route('/summary')
@login_required
def summary():
    try:
        total_items = inventory_collection.count_documents({})
        low_stock_items = inventory_collection.count_documents({"quantity": {"$lt": 5}})
        
        return render_template('summary.html', 
                               total_items_count=total_items,
                               low_stock_items_count=low_stock_items)
    except Exception as e:
        logging.error(f"Error loading summary page: {str(e)}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('home'))

@app.route('/')
@login_required
def index():
    return redirect(url_for('summary'))

if __name__ == '__main__':
    app.run(debug=True)
