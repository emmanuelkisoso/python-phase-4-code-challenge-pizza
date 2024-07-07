#!/usr/bin/env python3
import os
from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code Challenge</h1>"

class RestaurantsAPI(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        restaurants_data = [restaurant.to_dict() for restaurant in restaurants]
        return make_response(restaurants_data, 200)

class RestaurantAPI(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            restaurant_data = restaurant.to_dict()
            restaurant_data['restaurant_pizzas'] = [rp.to_dict() for rp in restaurant.restaurantpizzas]
            return make_response(restaurant_data, 200)
        return make_response({"error": "Restaurant not found"}, 404)

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response("", 204)
        return make_response({"error": "Restaurant not found"}, 404)

class PizzasAPI(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        pizzas_data = [pizza.to_dict() for pizza in pizzas]
        return make_response(pizzas_data, 200)

class RestaurantPizzasAPI(Resource):
    def post(self):
        data = request.get_json()
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        if not all([price, pizza_id, restaurant_id]):
            return make_response({"errors": ["price, pizza_id, and restaurant_id are required"]}, 400)

        if not (1 <= price <= 30):
            return make_response({"errors": ["price must be between 1 and 30"]}, 400)

        pizza = db.session.get(Pizza, pizza_id)
        restaurant = db.session.get(Restaurant, restaurant_id)

        if not pizza or not restaurant:
            return make_response({"errors": ["Invalid pizza_id or restaurant_id"]}, 400)

        new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(new_restaurant_pizza)
        db.session.commit()

        response_data = new_restaurant_pizza.to_dict()
        return make_response(response_data, 201)

api.add_resource(RestaurantsAPI, '/restaurants')
api.add_resource(RestaurantAPI, '/restaurants/<int:id>')
api.add_resource(PizzasAPI, '/pizzas')
api.add_resource(RestaurantPizzasAPI, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
