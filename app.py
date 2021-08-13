import requests # to call API 
from requests import Response # to call API 
from flask import Flask, url_for, render_template, request, redirect
from flask import Flask
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

    def __init__(self, user_name, age, gender, diabetes, allergies, activeness):
        self.user_name = user_name
        self.age = age
        self.gender = gender
        self.diabetes = diabetes
        self.allergies = allergies
        self.activeness = activeness

db.create_all()

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route('/search', methods=["GET","POST"])
def call_api():
    getData = request.form.get("search_keyword")
    app_id = 'f14b30eb'
    app_key = 'b09c4ad7a4f756f820de23a47aa49963'
    makeRequest: Response = requests.get('https://api.edamam.com/api/recipes/v2?type=public&q={}&app_id={}&app_key={}'.format(getData, app_id, app_key))
    search_data = makeRequest.json()
    # https: // api.edamam.com / api / recipes / v2?type = public & q = pizza & app_id = f14b30eb & app_key = b09c4ad7a4f756f820de23a47aa49963
    # return render_template("search.html", label=search_data['hits'][0]['recipe']['label'], ingredients = search_data['hits'][0]['recipe']['ingredientLines'])
    return render_template("search.html", search_data = search_data, getData=getData)
#     if else statmement  - diabetes yes else...
#  another condition for allergies yes
# another condition for both etc...

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

@app.route('/nhs')
def nhs():
    return render_template("nhs.html")

if __name__ == '__main__':
    db.create_all()
    app.debug = True
    app.run()

