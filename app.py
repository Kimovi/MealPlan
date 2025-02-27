import requests
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import ast

app = Flask(__name__, template_folder='./templates', static_folder='./static')

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(100))
    diabetes = db.Column(db.String(100))
    allergies = db.Column(db.String(100))
    activeness = db.Column(db.Integer)
    food_data = db.Column(db.Integer, db.ForeignKey('food.food_id'))

    def __init__(self, user_name, age, gender, diabetes, allergies, activeness):
        self.user_name = user_name
        self.age = age
        self.gender = gender
        self.diabetes = diabetes
        self.allergies = allergies
        self.activeness = activeness

class Food(db.Model):
    food_id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(200))
    calories = db.Column(db.Integer)
    date = db.Column(db.String(50))
    user_name = db.Column(db.String(100))
    user_id = db.relationship('Users', backref='food')

    def __init__(self, food_name, calories, date, user_name):
        self.food_name = food_name
        self.calories = calories
        self.date = date
        self.user_name = user_name

db.create_all()

@app.route("/")
def index_page():
    return render_template("index.html")

@app.route('/search', methods=["GET","POST"])
def search_page():
    users = db.session.query(Users)
    user_data = [dict(user_id=user.user_id,
                      user_name=user.user_name,
                      age=user.age,
                      gender=user.gender,
                      diabetes=user.diabetes,
                      allergies=user.allergies,
                      activeness=user.activeness
                      ) for user in users]

    search_keyword = request.form.get("search_keyword")
    diabetes = ''
    allergies = ''
    api_address = 'https://api.edamam.com/api/recipes/v2?type=public&'
    app_id = 'f14b30eb'
    app_key = 'b09c4ad7a4f756f820de23a47aa49963'
    selected_food = request.form.get("selected_food")
    selected_user = request.form.get("user_name")
    saved_selected_user = request.form.get("saved_selected_user")
    date = request.form.get("date")
    calories = request.form.get("calories")
    search_data = None

    # CHECK USER'S DIABETES/ALLERGIES OPTIONS
    if selected_user:
        for user in user_data:
            if user["user_name"] == selected_user:
                diabetes = user["diabetes"]
                allergies = user["allergies"]

    # FILTER DIABETES/ALLERGIES BY USER'S CHOICE
    if diabetes == 'Yes' and allergies == 'Peanut':
        result = requests.get('{}&q={}&app_id={}&app_key={}&diet=low-carb&health=peanut-free'.format(api_address, search_keyword, app_id, app_key))
        search_data = result.json()

    elif diabetes == 'Yes' and allergies == 'Crustacean':
        result = requests.get('{}&q={}&app_id={}&app_key={}&diet=low-carb&health=crustacean-free'.format(api_address, search_keyword, app_id, app_key))
        search_data = result.json()

    elif diabetes == 'Yes' and allergies == 'Gluten':
        result = requests.get('{}&q={}&app_id={}&app_key={}&diet=low-carb&health=gluten-free'.format(api_address, search_keyword, app_id, app_key))
        search_data = result.json()

    elif diabetes == 'No' and allergies == 'Peanut':
        result = requests.get('{}&q={}&app_id={}&app_key={}&health=peanut-free'.format(api_address, search_keyword, app_id, app_key))
        search_data = result.json()

    elif diabetes == 'No' and allergies == 'Crustacean':
        result = requests.get('{}&q={}&app_id={}&app_key={}&health=crustacean-free'.format(api_address, search_keyword, app_id, app_key))
        search_data = result.json()

    elif diabetes == 'No' and allergies == 'Gluten':
        result = requests.get('{}&q={}&app_id={}&app_key={}&health=gluten-free'.format(api_address, search_keyword, app_id, app_key))
        search_data = result.json()

    elif diabetes == 'No' and allergies == 'No-allergies':
        result = requests.get('{}&q={}&app_id={}&app_key={}'.format(api_address, search_keyword, app_id, app_key))
        search_data = result.json()

    # SAVE SELECTED FOOD NAME, INFO TO FOOD DB
    if selected_food:
        food_db = Food(food_name=selected_food,
                       calories=calories,
                       date=date,
                       user_name=saved_selected_user
                       )
        db.session.add(food_db)
        db.session.commit()

    # IF API SEARCH RESULT IS LESS THAN 10, THEN RETURN 'NO DATA' TO BE RENDERED
    if search_data !=None and search_data["count"] < 10:
        search_data = "No data"

    return render_template("search.html",
                           search_data=search_data,
                           search_keyword=search_keyword,
                           user_data=user_data,
                           selected_user=selected_user
                           )


@app.route('/users', methods=["GET", "POST"])
def users_page():
    if request.form:
        user_db = Users(user_name=request.form.get("user_name"),
                        age=request.form.get("age"),
                        gender=request.form.get("gender"),
                        diabetes=request.form.get("diabetes"),
                        allergies=request.form.get("allergies"),
                        activeness=request.form.get("activeness")
                        )
        db.session.add(user_db)
        db.session.commit()
    user_data = Users.query.all()
    return render_template("users.html", user_data=user_data)


@app.route('/delete_users', methods=["POST"])
def delete_user():
    if request.form:
        user_db = Users.query.filter_by(user_id=request.form.get("user_id")).first()
        db.session.delete(user_db)
        db.session.commit()
        return redirect("/users")


@app.route('/track', methods=["GET", "POST"])
def track_page():
    users = db.session.query(Users)
    users_data = [dict(user_name=user.user_name) for user in users]

    foods = db.session.query(Food)
    foods_data = [dict(food_id=item.food_id,
                       food_name=item.food_name,
                       calories=item.calories,
                       date=item.date,
                       user_name=item.user_name) for item in foods]

    filter_by_user = []
    selected_user = request.form.get("selected_name")
    if selected_user:
        selected_name = ast.literal_eval(selected_user)
        for item in foods_data:
            if item["user_name"] == selected_name["user_name"]:
                filter_by_user.append(item)
    return render_template("track.html", users_data=users_data, food_db=filter_by_user, get_user=selected_user)


@app.route('/delete_food', methods=["GET", "POST"])
def delete_food():
    if request.form:
        food_db = Food.query.filter_by(food_id=request.form.get("food_id")).first()
        db.session.delete(food_db)
        db.session.commit()
        return redirect("/track")


@app.route('/calculateBMI', methods=["GET", "POST"])
def calculateBMI_page():
    users = db.session.query(Users)
    user_data = [dict(user_name=user.user_name) for user in users]
    weight = request.form.get("Weight")
    height = request.form.get("Height")
    bmi=None

    if weight and height:
        bmi = calculate_bmi(weight, height)
        print(bmi)
        print(type(bmi))
    return render_template("calculateBMI.html", user_data=user_data, bmi=bmi)


def calculate_bmi(weight, height):
    try:
        bmi = round((float(weight)) / (float(height) * float(height)),2)
    except ZeroDivisionError:
        print('Please enter a valid input as weight')
    else:
        print(f"Your BMI is {bmi}")
    return bmi

if __name__ == '__main__':
    db.create_all()
    app.debug = True
    app.run()

