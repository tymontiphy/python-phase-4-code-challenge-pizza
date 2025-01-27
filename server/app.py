# #!/usr/bin/env python3
# from models import db, Restaurant, RestaurantPizza, Pizza
# from flask_migrate import Migrate
# from flask import Flask, request, make_response
# from flask_restful import Api, Resource
# import os

# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.json.compact = False

# migrate = Migrate(app, db)

# db.init_app(app)

# api = Api(app)


# @app.route("/")
# def index():
#     return "<h1>Code challenge</h1>"


# if __name__ == "__main__":
#     app.run(port=5555, debug=True)
#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
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

# GET / restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])

# GET /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    # Replace `query.get()` with `db.session.get()`
    restaurant = db.session.get(Restaurant, id)  # Updated method to avoid deprecation warning
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    # Get the restaurant's pizzas
    restaurant_data = restaurant.to_dict()
    restaurant_pizzas = [
        {
            "id": rp.id,
            "pizza": rp.pizza.to_dict(),
            "pizza_id": rp.pizza_id,
            "price": rp.price,
            "restaurant_id": rp.restaurant_id 
        }
        for rp in restaurant.pizzas
    ]
    restaurant_data["restaurant_pizzas"] = restaurant_pizzas 

    return jsonify(restaurant_data)


# DELETE /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    # Replace `query.get()` with `db.session.get()`
    restaurant = db.session.get(Restaurant, id)  # Updated method to avoid deprecation warning
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    # Delete the associated restaurant pizzas
    for rp in restaurant.pizzas:
        db.session.delete(rp)

    # Delete the restaurant
    db.session.delete(restaurant)
    db.session.commit()

    return '', 204

# GET /pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])

# POST /restaurant_pizzas
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    # Validate price
    if price is None or not (1 <= price <= 30):
        return jsonify({"errors": ["validation errors"]}), 400

    # Validate pizza and restaurant existence
    pizza = db.session.get(Pizza, pizza_id)  # Updated method to avoid deprecation warning
    restaurant = db.session.get(Restaurant, restaurant_id)  # Updated method to avoid deprecation warning
    if not pizza or not restaurant:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        # Create the new RestaurantPizza
        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(restaurant_pizza)
        db.session.commit()

        # Return the created RestaurantPizza with associated data
        response_data = restaurant_pizza.to_dict()
        response_data["pizza"] = pizza.to_dict()
        response_data["restaurant"] = restaurant.to_dict()
        return jsonify(response_data), 201

    except Exception as e:
        # Handle unexpected errors (e.g., database errors)
        return jsonify({"errors": ["validation errors"]}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)