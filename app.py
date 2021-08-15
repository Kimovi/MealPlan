import requests
from requests import Response
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

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
    # food_data = db.relationship('Food', backref='users')

    def __init__(self, user_name, age, gender, diabetes, allergies, activeness):
        self.user_name = user_name
        self.age = age
        self.gender = gender
        self.diabetes = diabetes
        self.allergies = allergies
        self.activeness = activeness

# class Food(db.Model):
#     food_id = db.Column(db.Integer, primary_key=True)
#     food_name = db.Column(db.String(200))
#     calories = db.Column(db.Integer)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
#
#     def __init__(self, food_id, food_name, calories):
#         self.food_id = food_id
#         self.food_name = food_name
#         self.calories = calories


db.create_all()

@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route('/search', methods=["GET","POST"])
def call_api():
    users = db.session.query(Users)
    user_data = [dict(user_name=user.user_name,
                      age=user.age,
                      gender=user.gender,
                      diabetes=user.diabetes,
                      allergies=user.allergies,
                      activeness=user.activeness
                      ) for user in users]
    selected_user = request.form.get("user_name")
    search_keyword = request.form.get("search_keyword")
    diabetes = ''
    allergies = ''

    app_id = 'f14b30eb'
    app_key = 'b09c4ad7a4f756f820de23a47aa49963'



    # 1. Diabetes and No allergies --> later
    # 2. Diabetes and Peanut
    # 3. Diabetes and Seafood
    # 4. Diabetes and Gluten
    # 5. No Diabetes no allergies --- > do this later!

    if selected_user:
        for user in user_data:
            if user["user_name"] == selected_user:
                diabetes = user["diabetes"]
                allergies = user["allergies"]

    print('user data from the DB: ',user_data, "\nSelected user: ", selected_user, "\nSearch keyword", search_keyword)
    print(diabetes, allergies)


    if diabetes == 'Yes' and allergies == 'Peanut-Free':
        print('hi')
        result = requests.get('https://api.edamam.com/api/recipes/v2?type=public&q={}&app_id=f14b30eb&app_key=b09c4ad7a4f756f820de23a47aa49963&diet=low-carb&health=peanut-free'.format(search_keyword))
        search_data = result.json()

    elif diabetes == 'Yes' and allergies == 'Crustacean-Free':
        result = requests.get('https://api.edamam.com/api/recipes/v2?type=public&q={}&app_id=f14b30eb&app_key=b09c4ad7a4f756f820de23a47aa49963&diet=low-carb&health=crustacean-free'.format(search_keyword))
        search_data = result.json()

    elif diabetes == 'Yes' and allergies == 'Gluten-Free':
        result = requests.get('https://api.edamam.com/api/recipes/v2?type=public&q={}&app_id=f14b30eb&app_key=b09c4ad7a4f756f820de23a47aa49963&diet=low-carb&health=gluten-free'.format(search_keyword))
        search_data = result.json()

    elif diabetes == 'No' and allergies == 'No-allergies':
        result = requests.get('https://api.edamam.com/api/recipes/v2?type=public&q={}&app_id=f14b30eb&app_key=b09c4ad7a4f756f820de23a47aa49963'.format(search_keyword))
        search_data = result.json()


    # makeRequest: Response = requests.get('https://api.edamam.com/api/recipes/v2?type=public&q={}&app_id={}&app_key={}'.format(search_keyword, app_id, app_key),params=payload)
    # search_data = makeRequest.json()

    # https://api.edamam.com/api/recipes/v2?type=public&q=pizza&app_id=f14b30eb&app_key=b09c4ad7a4f756f820de23a47aa49963
    # https://api.edamam.com/api/recipes/v2?type=public&q=pizza&app_id=f14b30eb&app_key=b09c4ad7a4f756f820de23a47aa49963&health=peanut-free
    # https://api.edamam.com/api/recipes/v2?type=public&q=pizza&app_id=f14b30eb&app_key=b09c4ad7a4f756f820de23a47aa49963&diet=low-carb&health=peanut-free

    return render_template("search.html",
                           search_data=search_data,
                           search_keyword=search_keyword,
                           user_data=user_data
                           )


@app.route('/users', methods=["GET", "POST"])
def users():
    if request.form:
        user_db = Users(user_name = request.form.get("user_name"),
                        age = request.form.get("age"),
                        gender=request.form.get("gender"),
                        diabetes=request.form.get("diabetes"),
                        allergies=request.form.get("allergies"),
                        activeness=request.form.get("activeness")
                        )
        db.session.add(user_db)
        db.session.commit()
    user_data = Users.query.all()
    return render_template("users.html", user_data = user_data)


@app.route('/delete_users', methods=["POST"])
def delete_user():
    if request.form:
        user_db = Users.query.filter_by(user_id=request.form.get("user_id")).first()
        db.session.delete(user_db)
        db.session.commit()
        return redirect("/users")


@app.route('/track', methods=["GET", "POST"])
def track():
    users = db.session.query(Users)
    users_data = [dict(user_name=user.user_name, age=user.age) for user in users]

    return render_template("track.html", users_data=users_data)


@app.route('/nhs')
def nhs():
    return render_template("nhs.html")


if __name__ == '__main__':
    db.create_all()
    app.debug = True
    app.run()

