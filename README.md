# Inventory Management System

Welcome to the Inventory Management System project! This is a web-based application designed to help businesses manage their inventory, sales, purchases, and more. The system is built using Flask for the backend and will have a responsive frontend for seamless user experience.

## Current Features

### Backend:
**Flask Framework:** The backend is built using Flask.
**Database Integration:** Successfully connected Flask to a MongoDB database using pymongo.
**Models:**
	•	Item: Represents individual items with fields for name, quantity, price, and description.
	•	User Authentication: Users can register, log in, and log out using the Flask-Login extension.
	•	CRUD Operations: Users can add, update, search, and delete inventory items from the system.

### Frontend:
**Bootstrap:** Utilized Bootstrap for responsive design.
**Item Listing:** The inventory list is dynamically updated with sorting and search functionalities.
**User Interface:** Forms for adding and updating items, along with buttons for editing and deleting.


## Getting Started

### Prerequisites:
• Python 3.11
• Flask 3.0.3
• MongoDB (running locally or on the cloud)
• Git 

### Setup Instructions
   **1.	Clone the repository:**
  ``` 
    git clone git@github.com:MbHashi/inventory-management-system.git
    cd inventory-management-system
  ```

   **2. Create a virtual environment:**
   ```
    python3 -m venv venv
    source venv/bin/activate
   ```


   **3.	Configure MongoDB:**
      Ensure that MongoDB is installed and running. Modify the connection string in the db.py file if necessary.
      You can create a MongoDB database with the following commands::
   ```
    use inventorydb
    db.createUser({
      user: "inventory_user",
      pwd: "YourPassword",
      roles: [{ role: "readWrite", db: "inventorydb" }]
    })
   ```


   **4.	Set up environment variables:**
   ```
    FLASK_APP=app.py
    FLASK_ENV=development
    SECRET_KEY=your_secret_key
    MONGO_URI=mongodb://localhost:27017/inventorydb
   ```


  **5. Start the development server:**
   ```
    flask run
   ```

  **6. Access the application:**
  Go to http://127.0.0.1:5000/ in your browser.

### Usage
  **Add Items:** Use the form on the main page to add new inventory items.
	**Search:** Search for items by name or description.
	**Edit Items:** Click on the “Edit” button next to an item to update its details.
	**Delete Items:** Click on the “Delete” button next to an item to remove it from the database.

### Frontend Features:
  **Bootstrap for Design:** The app uses Bootstrap 4 for a clean, responsive user interface.
	**DataTable for Inventory List:** The inventory list is powered by DataTables, enabling sorting, filtering, and pagination.

### Deployment

Instructions for deploying this project will be provided once the system is ready for production.




