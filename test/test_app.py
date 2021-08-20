import unittest
from CFGproject.app import app, db, Users, Food, calculate_bmi
from flask_testing import TestCase
from flask import url_for


class TestBase(TestCase):
    def create_app(self):
        app.config.update(SQLAlCHEMY_DATABASE_URI="sqlite:////tmp/test.db")
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        return app

    def setUp(self):
        db.create_all()
        user_sample = Users(user_name="BurgerKing",
                            age=14,
                            gender="female",
                            diabetes="Yes",
                            allergies="Peanut",
                            activeness=5
                            )

        food_sample = Food(food_name='Chicken',
                           calories=3500,
                           date='2021-08-21',
                           user_name='BurgerKing')

        db.session.add(user_sample)
        db.session.add(food_sample)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestPages(TestBase):
    def test_access_home(self):
        response = self.client.get(url_for('index_page'))
        self.assertEqual(response.status_code, 200)

    def test_search_page_is_displayed(self):
        response = self.client.get(url_for('search_page'))
        self.assertEqual(response.status_code, 200)

    def test_users_page_displayed(self):
        response = self.client.get(url_for('users_page'))
        self.assertEqual(response.status_code, 200)

    def test_track_page_is_displayed(self):
        response = self.client.get(url_for('track_page'))
        self.assertEqual(response.status_code, 200)

    def test_calculateBMI_page_is_displayed(self):
        response = self.client.get(url_for('calculateBMI_page'))
        self.assertEqual(response.status_code, 200)

    def test_calculate_bmi(self, weight=75, height=1.75):
        expected = 24.49  # --> 75/3.0625
        bmi = calculate_bmi(weight, height)
        self.assertEqual(expected, bmi)


class TestDB(TestBase):
    def test_delete_user(self):
        response = self.client.post(
            url_for('delete_user'),
            data=dict(user_id=1),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)


    def test_delete_food(self):
        response = self.client.post(
            url_for('delete_food'),
            data=dict(food_id=1),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)




