#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants")
def get_restaurants():
    restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
    return make_response((restaurants), 200)

@app.route("/restaurants/<int:id>" , methods = ['GET', 'DELETE'])
def restaurants_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()

    if request.method == 'GET':
        if restaurant:
            restaurant_dict = restaurant.to_dict()

            response = make_response(
                restaurant_dict,
                200,
                {"Content-Type": "application/json"}
            )
        else:
            response = make_response(
                {"error": "Restaurant not found"},
                404,
                {"Content-Type": "application/json"}
            )
    elif request.method == 'DELETE':
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            response = make_response(
                "",
                204,
                {"Content-Type": "application/json"}
            )
        else:
            response =make_response(
                {"error":"Restaurant was not found"},
                204,
                {"Content-Type": "application/json"}
            )
    return response

@app.route("/pizzas")
def get_pizzas():
    pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]
    return make_response((pizzas), 200)

@app.route("/restaurant_pizzas", methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    if not all([price, pizza_id, restaurant_id]):
        return make_response({"errors": ["price, pizza_id, and restaurant_id are required"]}, 400)

    pizza = Pizza.query.filter_by(id=pizza_id).first()
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()

    if not pizza or not restaurant:
        return make_response({"errors": ["Invalid pizza_id or restaurant_id"]}, 400)

    new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
    db.session.add(new_restaurant_pizza)
    db.session.commit()

    response_data = new_restaurant_pizza.to_dict()
    response_data['pizza'] = pizza.to_dict()
    response_data['restaurant'] = restaurant.to_dict()

    return make_response((response_data), 201)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
