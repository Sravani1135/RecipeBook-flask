import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# MongoDB configuration
app.config["MONGO_URI"] = os.getenv('MONGO_URI', "mongodb://localhost:27017/recipe_book")
mongo = PyMongo(app)

# Image upload configuration
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def initialize_sample_recipes():
    if mongo.db.recipes.count_documents({}) == 0:
        sample_recipes = [
            {
                "title": "Creamy Pasta Carbonara",
                "ingredients": [
                    "400g spaghetti",
                    "200g pancetta or guanciale, diced",
                    "4 large eggs",
                    "50g pecorino cheese, grated",
                    "50g parmesan, grated",
                    "Freshly ground black pepper",
                    "Salt to taste"
                ],
                "instructions": """1. Cook pasta in boiling salted water until al dente
2. Fry pancetta until crispy
3. Whisk eggs and cheeses together
4. Drain pasta, reserving some water
5. Quickly mix hot pasta with egg mixture
6. Add pancetta and mix well
7. Season with black pepper and salt""",
                "prep_time": 15,
                "cook_time": 15,
                "servings": 4,
                "difficulty": "medium",
                "tags": ["pasta", "italian", "dinner"],
                "image": "imgPasta.jpg",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "title": "Authentic Chicken Curry",
                "ingredients": [
                    "1kg chicken, cut into pieces",
                    "2 onions, finely chopped",
                    "4 garlic cloves, minced",
                    "2 tbsp ginger paste",
                    "3 tomatoes, pureed",
                    "2 tbsp curry powder",
                    "1 tsp turmeric",
                    "1 cup coconut milk",
                    "Fresh coriander for garnish"
                ],
                "instructions": """1. Heat oil in a pan and sauté onions until golden
2. Add garlic and ginger, cook for 2 minutes
3. Add chicken pieces and brown on all sides
4. Stir in spices and cook for 1 minute
5. Add tomato puree and simmer for 10 minutes
6. Pour in coconut milk and cook for 15 more minutes
7. Garnish with fresh coriander""",
                "prep_time": 20,
                "cook_time": 40,
                "servings": 4,
                "difficulty": "medium",
                "tags": ["chicken", "indian", "curry"],
                "image": "imgChickenCurry.jpg",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "title": "Avocado Toast with Poached Egg",
                "ingredients": [
                    "2 slices sourdough bread",
                    "1 ripe avocado",
                    "2 eggs",
                    "1 tbsp lemon juice",
                    "Red pepper flakes",
                    "Salt and pepper to taste",
                    "Microgreens for garnish"
                ],
                "instructions": """1. Toast bread until golden and crisp
2. Mash avocado with lemon juice, salt and pepper
3. Poach eggs in simmering water for 3-4 minutes
4. Spread avocado mixture on toast
5. Top with poached eggs
6. Sprinkle with red pepper flakes and microgreens""",
                "prep_time": 10,
                "cook_time": 10,
                "servings": 2,
                "difficulty": "easy",
                "tags": ["breakfast", "healthy", "vegetarian"],
                "image": "imgAvacadoegg.jpg",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        mongo.db.recipes.insert_many(sample_recipes)

initialize_sample_recipes()



@app.route('/')
def home1():
    return redirect(url_for('login'))
@app.route('/home')
def home():
    return redirect(url_for('main'))
@app.route('/space')
def space():
    recipes = list(mongo.db.recipes.find().sort("created_at", -1))
    username = session.get('username')

    # fallback if session doesn't have it:
    if not username and 'email' in session:
        user = mongo.db.users.find_one({'email': session['email']})
        if user:
            username = user.get('username')
            session['username'] = username  # store for next time

    return render_template('index.html', recipes=recipes, username=username)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    
    if not query:
        flash('Please enter a search term', 'warning')
        return redirect(url_for('index'))
    
    # Search in title, tags, and ingredients
    recipes = list(mongo.db.recipes.find({
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"tags": {"$regex": query, "$options": "i"}},
            {"ingredients": {"$regex": query, "$options": "i"}}
        ]
    }).sort("created_at", -1))
    
    return render_template('search.html', recipes=recipes, query=query)


@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        recipe = {
            'title': request.form.get('title'),
            'ingredients': [ing.strip() for ing in request.form.get('ingredients').split('\n') if ing.strip()],
            'instructions': request.form.get('instructions'),
            'prep_time': int(request.form.get('prep_time', 0)),
            'cook_time': int(request.form.get('cook_time', 0)),
            'servings': int(request.form.get('servings', 1)),
            'difficulty': request.form.get('difficulty', 'medium'),
            'tags': [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()],
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        image = request.files.get('image')
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            recipe['image'] = filename
        
        mongo.db.recipes.insert_one(recipe)
        flash('Recipe added successfully!', 'success')
        return redirect(url_for('space'))
    
    return render_template('add_recipe.html')

@app.route('/recipe/<recipe_id>')
def recipe(recipe_id):
    try:
        # Try to fetch from MongoDB by ObjectId
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        if recipe:
            return render_template('recipe_detail.html', recipe=recipe)
    except:
        pass  # It's okay if it's not a valid ObjectId

    # Fallback: check if it's a hardcoded demo ID (like "1", "2", etc.)
    demo_recipes = {
    "1": {
        "title": "Bruschetta",
        "ingredients": ["Tomatoes", "Basil", "Olive Oil", "Bread"],
        "instructions": "Chop tomatoes and basil, mix with olive oil, serve on toasted bread.",
        "prep_time": 10,
        "cook_time": 5,
        "servings": 2,
        "difficulty": "easy",
        "tags": ["starter", "italian"],
        "image": "imageBruschita.jpg"
    },
    "2": {
        "title": "Stuffed Mushrooms",
        "ingredients": ["Mushrooms", "Cream Cheese", "Garlic"],
        "instructions": "Stuff mushrooms with cream cheese and garlic, bake until golden.",
        "prep_time": 15,
        "cook_time": 20,
        "servings": 4,
        "difficulty": "easy",
        "tags": ["starter", "baked"],
        "image": "imageStuffedMush.jpg"
    },
    "3": {
        "title": "Caprese Salad",
        "ingredients": ["Mozzarella", "Tomatoes", "Basil"],
        "instructions": "Layer tomatoes, mozzarella, and basil. Drizzle with olive oil and serve cold.",
        "prep_time": 5,
        "cook_time": 0,
        "servings": 2,
        "difficulty": "easy",
        "tags": ["starter", "fresh", "italian"],
        "image": "imgCapraseSalad.jpg"
    },
    "4": {
        "title": "Grilled Chicken",
        "ingredients": ["Chicken", "Olive Oil", "Garlic", "Spices"],
        "instructions": "Marinate chicken with spices and grill until cooked through.",
        "prep_time": 20,
        "cook_time": 25,
        "servings": 3,
        "difficulty": "medium",
        "tags": ["main", "grilled"],
        "image": "imgGrilledChick.jpg"
    },
    "5": {
        "title": "Vegetable Stir Fry",
        "ingredients": ["Mixed Vegetables", "Soy Sauce", "Garlic", "Ginger"],
        "instructions": "Quick-fry vegetables with soy sauce and serve hot.",
        "prep_time": 10,
        "cook_time": 10,
        "servings": 2,
        "difficulty": "easy",
        "tags": ["main", "vegetarian"],
        "image": "imgVegStirFry.jpg"
    },
    "6": {
        "title": "Spaghetti Carbonara",
        "ingredients": ["Spaghetti", "Eggs", "Parmesan", "Bacon"],
        "instructions": "Mix cooked spaghetti with eggs, cheese, and crispy bacon.",
        "prep_time": 15,
        "cook_time": 15,
        "servings": 4,
        "difficulty": "medium",
        "tags": ["main", "pasta"],
        "image": "imgSpageti.jpg"
    },
    "7": {
        "title": "Chocolate Cake",
        "ingredients": ["Cocoa Powder", "Flour", "Sugar", "Eggs", "Butter"],
        "instructions": "Mix ingredients, pour into pan, and bake until set.",
        "prep_time": 20,
        "cook_time": 30,
        "servings": 8,
        "difficulty": "medium",
        "tags": ["dessert", "baking"],
        "image": "imgDBC.jpg"
    },
    "8": {
        "title": "Fruit Tart",
        "ingredients": ["Pastry", "Fresh Fruits", "Custard"],
        "instructions": "Fill baked pastry with custard and top with sliced fruits.",
        "prep_time": 25,
        "cook_time": 10,
        "servings": 6,
        "difficulty": "medium",
        "tags": ["dessert", "fruit"],
        "image": "imgFruitTart.jpg"
    },
    "9": {
        "title": "Cheesecake",
        "ingredients": ["Cream Cheese", "Eggs", "Sugar", "Graham Cracker Crust"],
        "instructions": "Bake cream cheese mixture over crust and chill before serving.",
        "prep_time": 30,
        "cook_time": 45,
        "servings": 8,
        "difficulty": "medium",
        "tags": ["dessert", "baking"],
        "image": "imgCheesecake.jpg"
    }
}


    if recipe_id in demo_recipes:
        return render_template('recipe_detail.html', recipe=demo_recipes[recipe_id])

    flash('Recipe not found', 'danger')
    return render_template('not_found.html'), 404
@app.route('/edit/<recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if not recipe:
        flash('Recipe not found', 'danger')
        return render_template('not_found.html'), 404
    
    if request.method == 'POST':
        update_data = {
            'title': request.form.get('title'),
            'ingredients': [ing.strip() for ing in request.form.get('ingredients').split('\n') if ing.strip()],
            'instructions': request.form.get('instructions'),
            'prep_time': int(request.form.get('prep_time', 0)),
            'cook_time': int(request.form.get('cook_time', 0)),
            'servings': int(request.form.get('servings', 1)),
            'difficulty': request.form.get('difficulty', 'medium'),
            'tags': [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()],
            'updated_at': datetime.now()
        }
        
        image = request.files.get('image')
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            update_data['image'] = filename
        
        mongo.db.recipes.update_one(
            {"_id": ObjectId(recipe_id)},
            {"$set": update_data}
        )
        flash('Recipe updated successfully!', 'success')
        return redirect(url_for('recipe', recipe_id=recipe_id))
    
    return render_template('edit_recipe.html', recipe=recipe)

@app.route('/delete/<recipe_id>')
def delete_recipe(recipe_id):
    result = mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
    if result.deleted_count > 0:
        flash('Recipe deleted successfully!', 'success')
    else:
        flash('Recipe not found', 'danger')
    return redirect(url_for('space'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['uname']
        email = request.form['uemail']
        password = request.form['upwd']

        if mongo.db.users.find_one({'email': email}):
            flash('Email already registered!', 'warning')
            
            return redirect(url_for('login'))  # not render_template


        hashed_pw = generate_password_hash(password)
        mongo.db.users.insert_one({'username': uname, 'email': email, 'password': hashed_pw})
        # 🔥 Save to session here:
        session['email'] = email
        session['username'] = uname  # this line adds the welcome name!

        flash('Registration successful!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')
@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['pemail']
        password = request.form['ppwd']

        user = mongo.db.users.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['email'] = email
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')
@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('main'))
    return redirect(url_for('main'))
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))
@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('forgot_password'))

        user = mongo.db.users.find_one({'email': email})
        if not user:
            flash('No account found with that email.', 'warning')
            return redirect(url_for('forgot_password'))

        hashed_pw = generate_password_hash(new_password)
        mongo.db.users.update_one({'email': email}, {'$set': {'password': hashed_pw}})
        flash('Password reset successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('forgot.html')

@app.route('/submit_doubt', methods=['POST'])
def submit_doubt():
    doubt = {
        "email": request.form.get("previous_email"),
        "query": request.form.get("query"),
        "phone": request.form.get("phone"),
        "category": request.form.get("doubts"),
        "submitted_at": datetime.now()
    }
    mongo.db.doubts.insert_one(doubt)
    flash("Your doubt has been submitted successfully!", "success")
    return redirect(url_for('main'))  # or wherever you want to go after

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
#this is up to
import os
app.config["MONGO_URI"] = os.getenv('MONGO_URI')
app.secret_key = os.getenv('SECRET_KEY')
